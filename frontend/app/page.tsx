'use client'

import { useState, useEffect } from 'react'
import Navbar from "./components/navbar"
import Hero from "./components/hero"
import Logout from "./components/logout"
import Analytics from "./components/analytics"
import axios from '@/lib/axios'

export default function Home() {
  const [userRole, setUserRole] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUserRole = async () => {
      try {
        const response = await axios.get('/users/me')
        setUserRole(response.data)
      } catch (error) {
        setUserRole(null)
      } finally {
        setLoading(false)
      }
    }
    fetchUserRole()
  }, [])

  if (loading) {
    return (
      <>
        <Navbar />
        <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
          <p className="text-white text-xl">Loading...</p>
        </section>
      </>
    )
  }

  return (
    <>
      <Navbar />
      {userRole?.role === 'trainer' ? (
        <Analytics />
      ) : (
        <Hero user={userRole} />
      )}
      <Logout />
    </>
  )
}