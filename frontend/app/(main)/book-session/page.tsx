'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from '@/lib/axios'
import { useRouter } from 'next/navigation'

interface Availability {
    id: string
    trainer_id: string
    booking_date: string
    start_time: string
    end_time: string
}

interface Trainer {
    id: string
    name: string
    email: string
}

export default function BookSession() {
    const router = useRouter()
    const [selectedTrainer, setSelectedTrainer] = useState<string>('')
    const [availability, setAvailability] = useState<Availability[]>([])
    const [loading, setLoading] = useState(false)
    const [trainers, setTrainers] = useState<Trainer[]>([])
    const [currentUser, setCurrentUser] = useState<any>(null)

    useEffect(() => {
        fetchCurrentUser()
        fetchTrainers()
    }, [])

    const fetchCurrentUser = async () => {
        try {
            const response = await axios.get('/users/me')
            setCurrentUser(response.data)
        } catch (error) {
            console.error("Error fetching user:", error)
        }
    }

    const fetchTrainers = async () => {
        try {
            const response = await axios.get('/users/trainers')
            setTrainers(response.data)
        } catch (error) {
            console.error("Error fetching trainers:", error)
        }
    }

    const fetchAvailability = async (trainerId: string) => {
        setLoading(true)
        try {
            const response = await axios.get(`/availability/${trainerId}/available`)
            setAvailability(response.data)
        } catch (error) {
            console.error("Error fetching availability:", error)
            setAvailability([])
        } finally {
            setLoading(false)
        }
    }

    const handleBooking = async (avail: Availability) => {
        if (!currentUser?.id) {
            alert('Please log in to book a session')
            return
        }

        setLoading(true)
        try {
            console.log("Booking data:", {
                trainer_id: selectedTrainer,
                booking_date: avail.booking_date,
                start_time: avail.start_time,
                end_time: avail.end_time
            });
            await axios.post('/bookings/', {
                trainer_id: selectedTrainer,
                booking_date: avail.booking_date,
                start_time: avail.start_time,
                end_time: avail.end_time
            })
            alert('Booking request sent successfully!')
            router.push('/my-bookings')
        } catch (error: any) {
            console.error("Error booking session:", error)
            alert(error.response?.data?.detail || 'Failed to book session')
        } finally {
            setLoading(false)
        }
    }

    return (
        <>
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
                <div className="max-w-4xl w-full bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20">
                    <h1 className="text-3xl font-bold text-white mb-6 text-center">Book a Training Session</h1>

                    {/* Trainer Selection */}
                    <div className="mb-6 items-center flex flex-col space-y-3">
                        <label className="block text-white font-medium">Select Trainer</label>
                        <select
                            value={selectedTrainer}
                            onChange={(e) => setSelectedTrainer(e.target.value)}
                            className="w-full p-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="">Choose a trainer...</option>
                            {trainers.map((trainer) => (
                                <option key={trainer.id} value={trainer.id} className="text-gray-900">
                                    {trainer.name} ({trainer.email})
                                </option>
                            ))}
                        </select>
                        <button
                            type="button"
                            className="p-3 cursor-pointer bg-white text-black font-semibold rounded-lg shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-[1.02]"
                            onClick={() => selectedTrainer && fetchAvailability(selectedTrainer)}
                        >
                            Show Availability
                        </button>
                    </div>

                    {/* Display Availability */}
                    {loading && <p className="text-white text-center">Loading availability...</p>}

                    {availability.length > 0 && (
                        <div className="mb-6 p-4 bg-blue-600/30 rounded-lg border border-blue-400/30">
                            <h2 className="text-xl font-semibold text-white mb-3">Trainer Availability</h2>
                            <div className="text-white space-y-2 max-h-60 overflow-y-auto">
                                {availability.map((avail: Availability) => (
                                    <div key={avail.id} className="p-3 bg-white/10 rounded mb-2 flex justify-between items-center">
                                        <div>
                                            <p><strong>Date:</strong> {avail.booking_date}</p>
                                            <p><strong>Time:</strong> {avail.start_time} - {avail.end_time}</p>
                                        </div>
                                        <button
                                            onClick={() => handleBooking(avail)}
                                            disabled={loading}
                                            className='px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold'
                                        >
                                            {loading ? 'Booking...' : 'Book Session'}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {availability.length === 0 && selectedTrainer && !loading && (
                        <p className="text-white text-center">This trainer has no availability right now, come back later</p>
                    )}

                    <div className="mt-6 text-center">
                        <Link href="/my-bookings" className="text-blue-300 hover:text-blue-200 underline">
                            View My Bookings
                        </Link>
                    </div>
                </div>
            </section>
        </>
    )
}
