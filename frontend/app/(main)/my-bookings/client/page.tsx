'use client'

import { useEffect, useState } from 'react'
import axios from '@/lib/axios'
import { convert24To12 } from '@/lib/util'
import { useRouter } from 'next/navigation'

interface Booking {
    id: string
    trainer_id: string
    client_id: string
    booking_date: string
    start_time: string
    end_time: string
    status: 'pending' | 'confirmed' | 'cancelled'
    trainer_info: {
        name: string
        email: string
    }
}

export default function MyBookings() {
    const router = useRouter()
    const [bookingInfo, setBookingInfo] = useState<Booking[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchBookings();
    }, [])

    const fetchBookings = async () => {
        try {
            const response = await axios.get('/bookings/client')
            console.log('Response data:', response.data)
            setBookingInfo(response.data)
        } catch (error) {
            console.error('Error fetching bookings:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleCancelBooking = async (bookingId: string) => {
        if (!confirm('Are you sure you want to cancel this booking?')) return
        
        try {
            await axios.put(`/bookings/${bookingId}`, { status: 'cancelled' })
            fetchBookings()
        } catch (error) {
            console.error('Error cancelling booking:', error)
            alert('Failed to cancel booking')
        }
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'confirmed': return 'bg-green-500'
            case 'cancelled': return 'bg-red-500'
            case 'pending': return 'bg-yellow-500'
            default: return 'bg-gray-500'
        }
    }

    if (loading) {
        return (
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
                <p className="text-white text-xl">Loading bookings...</p>
            </section>
        )
    }

    return (
        <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-4">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-white mb-6">My Bookings</h1>

                {bookingInfo.length === 0 ? (
                    <p className="text-white">No bookings yet</p>
                ) : (
                    <div className="space-y-4">
                        {bookingInfo.filter(b => b.status !== 'cancelled').map(booking => {
                            const trainer = booking.trainer_info;
                            return (
                                <div key={booking.id} 
                                     className="cursor-pointer hover:scale-105 transition-transform bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20"
                                     onClick={() => router.push(`/my-bookings/client/workout-plans?trainer_id=${booking.trainer_id}`)}>
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-white font-semibold text-lg">
                                                {trainer.name || 'Unknown Trainer'}
                                            </p>
                                            <p className="text-blue-200 text-sm">
                                                {trainer.email || ''}
                                            </p>
                                            <p className="text-blue-200 text-sm mt-2">
                                                {booking.booking_date} | {convert24To12(booking.start_time)} - {convert24To12(booking.end_time)}
                                            </p>
                                            <div className="mt-2">
                                                <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${getStatusColor(booking.status)}`}>
                                                    {booking.status}
                                                </span>
                                            </div>
                                        </div>
                                        {booking.status === 'pending' && (
                                            <button
                                                onClick={() => handleCancelBooking(booking.id)}
                                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                                            >
                                                Cancel
                                            </button>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}
            </div>
        </section>
    )
}
