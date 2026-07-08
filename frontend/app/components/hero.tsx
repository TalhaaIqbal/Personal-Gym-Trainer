'use client'

import { useEffect, useState } from "react"
import axios from "@/lib/axios"

interface LoggedUser {
    id: string,
    email: string,
    role: "client" | "trainer" | "admin"
}

export default function Hero() {
  const [loggedUserData, setLoggedUserData] = useState<LoggedUser | null>(null)
        const fetchLoggedUser = async () => {
        try {
            const response = await axios.get('/users/me')
            setLoggedUserData(response.data)
        } catch (error) {
            console.error('Error fetching logged user:', error)
        }
    }

    useEffect(() => {
        fetchLoggedUser();
        console.log(loggedUserData)
    }, [])

  return (
    <>
        <section className="pt-20 flex flex-col items-center h-screen">
            <h1 className="flex flex-col items-center justify-center">Hero</h1>
            <p className="flex flex-col items-center justify-center">Hero description</p>
            {loggedUserData && (
                <p className="flex flex-col items-center justify-center">Logged in as: {loggedUserData.email}</p>
            )}
        </section>
    </>
  )
}