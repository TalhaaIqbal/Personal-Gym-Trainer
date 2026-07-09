'use client'

import { useEffect, useState } from 'react'
import axios from '@/lib/axios'
import { convert24To12 } from '@/lib/util'
import Link from 'next/link'

interface Booking {
    id: string
    trainer_id: string
    client_id: string
    booking_date: string
    start_time: string
    end_time: string
    status: 'pending' | 'confirmed' | 'cancelled'
    client_info?: {
        name: string
        email: string
    }
}

interface Availability {
    id: string
    trainer_id: string
    booking_date: string
    start_time: string
    end_time: string
}

export default function MyBookings() {
    const [bookings, setBookings] = useState<Booking[]>([])
    const [availability, setAvailability] = useState<Availability[]>([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState<'bookings' | 'availability'>('bookings')

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [bookingsResponse, availabilityResponse] = await Promise.all([
                axios.get('/bookings/trainer'),
                axios.get('/availability/me')
            ])
            setBookings(bookingsResponse.data)
            setAvailability(availabilityResponse.data)
        } catch (error) {
            console.error('Error fetching data:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleConfirmBooking = async (bookingId: string) => {
        try {
            await axios.put(`/bookings/${bookingId}`, { status: 'confirmed' })
            fetchData()
        } catch (error) {
            console.error('Error confirming booking:', error)
            alert('Failed to confirm booking')
        }
    }

    const handleRejectBooking = async (bookingId: string) => {
        if (!confirm('Are you sure you want to reject this booking?')) return
        try {
            await axios.put(`/bookings/${bookingId}`, { status: 'cancelled' })
            fetchData()
        } catch (error) {
            console.error('Error rejecting booking:', error)
            alert('Failed to reject booking')
        }
    }

    const handleCancelAvailability = async (availabilityId: string) => {
        if (!confirm('Are you sure you want to cancel this availability slot?')) return
        try {
            await axios.delete(`/availability/${availabilityId}`)
            fetchData()
        } catch (error) {
            console.error('Error cancelling availability:', error)
            alert('Failed to cancel availability')
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
                <p className="text-white text-xl">Loading...</p>
            </section>
        )
    }

    return (
        <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-4">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-white mb-6">My Dashboard</h1>

                {/* Tab Navigation */}
                <div className="flex space-x-4 mb-6">
                    <button
                        onClick={() => setActiveTab('bookings')}
                        className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                            activeTab === 'bookings'
                                ? 'bg-blue-600 text-white'
                                : 'bg-white/10 text-blue-200 hover:bg-white/20'
                        }`}
                    >
                        Bookings ({bookings.filter(b => b.status !== 'cancelled').length})
                    </button>
                    <button
                        onClick={() => setActiveTab('availability')}
                        className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                            activeTab === 'availability'
                                ? 'bg-blue-600 text-white'
                                : 'bg-white/10 text-blue-200 hover:bg-white/20'
                        }`}
                    >
                        Availability ({availability.length})
                    </button>
                </div>

                {activeTab === 'bookings' ? (
                    <>
                        <h2 className="text-2xl font-bold text-white mb-4">Client Bookings</h2>
                        {bookings.length === 0 ? (
                            <p className="text-white">No bookings yet</p>
                        ) : (
                            <div className="space-y-4">
                                {bookings.filter(b => b.status !== 'cancelled').map(booking => (
                                    <div key={booking.id} className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-white font-semibold text-lg">
                                                    {booking.client_info?.name || 'Unknown Client'}
                                                </p>
                                                <p className="text-blue-200 text-sm">
                                                    {booking.client_info?.email || ''}
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
                                            <div className="flex flex-col space-y-2">
                                                {booking.status === 'pending' && (
                                                    <div className="flex space-x-2">
                                                        <button
                                                            onClick={() => handleConfirmBooking(booking.id)}
                                                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                                                        >
                                                            Confirm
                                                        </button>
                                                        <button
                                                            onClick={() => handleRejectBooking(booking.id)}
                                                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                                                        >
                                                            Reject
                                                        </button>
                                                    </div>
                                                )}
                                                {booking.status === 'confirmed' && (
                                                    <Link
                                                        href={`/workout-plan-builder?client_id=${booking.client_id}`}
                                                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-center"
                                                    >
                                                        Create Workout Plan
                                                    </Link>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                ) : (
                    <>
                        <h2 className="text-2xl font-bold text-white mb-4">My Availability</h2>
                        {availability.length === 0 ? (
                            <p className="text-white">No availability set</p>
                        ) : (
                            <div className="space-y-4">
                                {availability.map(avail => (
                                    <div key={avail.id} className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-white font-semibold text-lg">
                                                    {avail.booking_date}
                                                </p>
                                                <p className="text-blue-200 text-sm mt-2">
                                                    {convert24To12(avail.start_time)} - {convert24To12(avail.end_time)}
                                                </p>
                                            </div>
                                            <button
                                                onClick={() => handleCancelAvailability(avail.id)}
                                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                )}
            </div>
        </section>
    )
}
