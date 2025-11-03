import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
import bcrypt from "bcryptjs"
import { prisma } from "@/lib/prisma"

// 개발자용 사용자 추가 함수 (관리자만 사용 가능)
export async function addUser(email: string, password: string, name: string, adminEmail: string) {
  // 관리자 권한 확인
  if (adminEmail !== process.env.ADMIN_EMAIL) {
    throw new Error('Unauthorized: Only admin can create users')
  }

  // 이메일 중복 확인
  const existingUser = await prisma.user.findUnique({
    where: { email }
  })

  if (existingUser) {
    throw new Error('User with this email already exists')
  }

  const hashedPassword = await bcrypt.hash(password, 12)

  const newUser = await prisma.user.create({
    data: {
      email,
      password: hashedPassword,
      name,
      role: 'user'
    }
  })

  return {
    id: newUser.id,
    email: newUser.email,
    name: newUser.name
  }
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string }
        })

        if (user && await bcrypt.compare(credentials.password as string, user.password)) {
          return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
          }
        }

        return null
      }
    })
  ],
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.role = user.role
      }
      return token
    },
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id as string
        session.user.role = token.role as string
      }
      return session
    },
  },
})