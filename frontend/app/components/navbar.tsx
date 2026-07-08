'use client'

import { useEffect, useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import axios from "@/lib/axios"

export default function Navbar() {
  const [userRole, setUserRole] = useState<string | null>(null)
  const pathname = usePathname()

  useEffect(() => {
    const fetchUserRole = async () => {
      try {
        const response = await axios.get('/users/me')
        setUserRole(response.data.role)
      } catch (error) {
        console.error('Error fetching user role:', error)
      }
    }
    fetchUserRole()
  }, [])

  const linkClass = (href: string) => {
    const isActive = pathname === href
    return `block py-2 px-4 rounded-lg transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25 ${
      isActive
        ? "text-white bg-blue-600/50 md:bg-blue-600/30"
        : "text-blue-100 hover:bg-blue-700/50 hover:text-white md:hover:bg-blue-700/30"
    }`
  }

  return (
    <>
      <nav className="fixed w-full z-20 top-0 start-0 bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 backdrop-blur-md border-b border-blue-700/50 shadow-lg">
        <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
          <Link href="/" className="flex items-center space-x-3 rtl:space-x-reverse group">
            <span className="self-center text-2xl font-bold text-white whitespace-nowrap group-hover:text-blue-200 transition-colors duration-300">GymTime</span>
          </Link>
          <div className="flex items-center md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
            <button type="button" className="flex text-sm bg-blue-700/50 rounded-full md:me-0 focus:ring-4 focus:ring-blue-500/50 hover:bg-blue-600/50 transition-all duration-300" id="user-menu-button" aria-expanded="false" data-dropdown-toggle="user-dropdown" data-dropdown-placement="bottom">
              <span className="sr-only">Open user menu</span>
            </button>
            <div className="z-50 hidden bg-blue-900/95 backdrop-blur-md border border-blue-600/50 rounded-xl shadow-2xl w-44" id="user-dropdown">
              <div className="px-4 py-3 text-sm border-b border-blue-700/50">
                <span className="block text-white font-medium">Joseph McFall</span>
                <span className="block text-blue-200 truncate">name@GymTime.com</span>
              </div>
              <ul className="p-2 text-sm text-blue-100 font-medium" aria-labelledby="user-menu-button">
                <li>
                  <Link href="#" className="inline-flex items-center w-full p-2 hover:bg-blue-700/50 hover:text-white rounded-lg transition-all duration-200">Settings</Link>
                </li>
                <li>
                  <Link href="/(auth)/login" className="inline-flex items-center w-full p-2 hover:bg-blue-700/50 hover:text-white rounded-lg transition-all duration-200">Sign out</Link>
                </li>
              </ul>
            </div>
            <button data-collapse-toggle="navbar-user" type="button" className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-blue-100 rounded-lg md:hidden hover:bg-blue-700/50 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-300" aria-controls="navbar-user" aria-expanded="false">
              <span className="sr-only">Open main menu</span>
              <svg className="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" strokeLinecap="round" strokeWidth="2" d="M5 7h14M5 12h14M5 17h14" /></svg>
            </button>
          </div>
          <div className="items-center justify-between hidden w-full md:flex md:w-auto md:order-1" id="navbar-user">
            <ul className="font-medium flex flex-col p-4 md:p-0 mt-4 border border-blue-700/50 rounded-xl bg-blue-800/50 backdrop-blur-md md:flex-row md:space-x-1 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-transparent">
              <li>
                <Link href="/" className={linkClass("/")}>Home</Link>
              </li>
              {userRole === 'trainer' && (
                <li>
                  <Link href="/trainer_availability" className={linkClass("/trainer_availability")}>Set Availability</Link>
                </li>
              )}
              {userRole === 'client' && (
                <li>
                  <Link href="/book-session" className={linkClass("/book-session")}>Book Session</Link>
                </li>
              )}
              <li>
                <Link href="/my-bookings" className={linkClass("/my-bookings")}>My Bookings</Link>
              </li>
              <li>
                <Link href="#" className={linkClass("#")}>Services</Link>
              </li>
              <li>
                <Link href="#" className={linkClass("#")}>Pricing</Link>
              </li>
              <li>
                <Link href="#" className={linkClass("#")}>Contact</Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </>
  )
}