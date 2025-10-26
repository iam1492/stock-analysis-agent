import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  // 환경 변수에서 관리자 계정 정보 가져오기
  const adminEmail = process.env.ADMIN_EMAIL
  const adminPassword = process.env.ADMIN_PASSWORD
  const adminName = process.env.ADMIN_NAME || 'Admin'

  if (!adminEmail || !adminPassword) {
    console.error('관리자 계정 생성을 위해 다음 환경 변수가 필요합니다:')
    console.error('- ADMIN_EMAIL: 관리자 이메일')
    console.error('- ADMIN_PASSWORD: 관리자 비밀번호')
    console.error('- ADMIN_NAME: 관리자 이름 (선택사항, 기본값: Admin)')
    console.error('')
    console.error('개발 환경에서는 .env.local 파일에 설정하세요.')
    console.error('프로덕션 환경에서는 Vercel 환경 변수에 설정하세요.')
    process.exit(1)
  }

  // 프로덕션 환경에서만 관리자 계정 생성 (보안 강화)
  if (process.env.NODE_ENV === 'production') {
    console.log('프로덕션 환경에서 관리자 계정을 생성합니다...')
  } else {
    console.log('개발 환경에서 관리자 계정을 생성합니다...')
  }

  // 기존 관리자 계정이 있는지 확인
  const existingAdmin = await prisma.user.findUnique({
    where: { email: adminEmail }
  })

  if (!existingAdmin) {
    const hashedPassword = await bcrypt.hash(adminPassword, 12)

    await prisma.user.create({
      data: {
        email: adminEmail,
        name: adminName,
        password: hashedPassword,
        role: 'admin'
      }
    })

    console.log('관리자 계정이 생성되었습니다:')
    console.log(`이메일: ${adminEmail}`)
    console.log(`이름: ${adminName}`)
    console.log(`역할: admin`)
  } else {
    console.log('관리자 계정이 이미 존재합니다.')
  }
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error(e)
    await prisma.$disconnect()
    process.exit(1)
  })