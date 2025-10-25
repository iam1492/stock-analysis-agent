import { NextRequest, NextResponse } from "next/server"
import { addUser, auth } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    // 개발 환경에서만 회원가입 허용
    if (process.env.NODE_ENV === 'production') {
      return NextResponse.json(
        { error: "User registration is not allowed in production" },
        { status: 403 }
      )
    }

    const { email, password, name } = await request.json()

    // 입력 검증
    if (!email || !password || !name) {
      return NextResponse.json(
        { error: "Email, password, and name are required" },
        { status: 400 }
      )
    }

    if (password.length < 6) {
      return NextResponse.json(
        { error: "Password must be at least 6 characters long" },
        { status: 400 }
      )
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: "Invalid email format" },
        { status: 400 }
      )
    }

    // 관리자 권한 확인을 위한 세션 정보 필요
    const session = await auth()
    if (!session?.user?.email || session.user.email !== process.env.ADMIN_EMAIL) {
      return NextResponse.json(
        { error: "Unauthorized: Only admin can create users" },
        { status: 403 }
      )
    }

    // 사용자 추가
    const newUser = await addUser(email, password, name, session.user.email)

    return NextResponse.json({
      message: "User created successfully",
      user: {
        id: newUser.id,
        email: newUser.email,
        name: newUser.name
      }
    })

  } catch (error) {
    console.error("Signup error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}