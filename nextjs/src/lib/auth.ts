import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
import bcrypt from "bcryptjs"

// 임시 사용자 저장소 (실제로는 데이터베이스를 사용해야 함)
const users = [
  {
    id: "1",
    email: "admin@example.com",
    password: "$2b$12$LXhRUPp4nSn2jfEew1/qi.ESOdnt61.ZyVW8Hh4PeJRaRXvxc3msq", // 해시된 "password123"
    name: "Admin User"
  }
]

// 개발자용 사용자 추가 함수 (개발 환경에서만 사용)
export async function addUser(email: string, password: string, name: string) {
  if (process.env.NODE_ENV === 'production') {
    throw new Error('User registration is not allowed in production')
  }

  const hashedPassword = await bcrypt.hash(password, 12)
  const newUser = {
    id: (users.length + 1).toString(),
    email,
    password: hashedPassword,
    name
  }

  users.push(newUser)
  return newUser
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

        const user = users.find(u => u.email === credentials.email)

        if (user && await bcrypt.compare(credentials.password as string, user.password)) {
          return {
            id: user.id,
            email: user.email,
            name: user.name,
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
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
      }
      return session
    },
  },
})