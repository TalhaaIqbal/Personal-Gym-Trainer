'use client'

import axios from "@/lib/axios"
import { useRouter } from "next/navigation"

export default function Logout() {
    const router = useRouter();

    const handleLogOut = async () => {
        try {
            await axios.post("/auth/logout")
        } catch (error) {
            console.error('Logout failed:', error)
        }
        finally {
            localStorage.removeItem("token");
            localStorage.removeItem("refreshToken");
            router.push("/login");
        }
    }

    return (
        <button
            onClick={handleLogOut}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 fixed bottom-4 right-4">
            Logout
        </button>
    )
}