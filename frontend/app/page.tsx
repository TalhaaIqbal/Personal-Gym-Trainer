'use client'

import Navbar from "./components/navbar"
import Hero from "./components/hero"
import Logout from "./components/logout"

export default function Home() {
  return (
    <>
      <Navbar />
      <Hero />
      <Logout />
    </>
  )
}