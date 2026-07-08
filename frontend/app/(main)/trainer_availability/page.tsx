'use client'

import React, { useEffect, useState } from 'react'
import axios from '@/lib/axios'
import { useRouter } from 'next/navigation'
import Navbar from '../../components/navbar'

interface CellKey {
    date: string      
    hour: number       
}

export default function TrainerAvailability() {
    const router = useRouter()
    const [currentUser, setCurrentUser] = useState<any>(null)
    const [loading, setLoading] = useState(false)
    const [selectedCells, setSelectedCells] = useState<Set<string>>(new Set())
    const [bookedSlots, setBookedSlots] = useState<Set<string>>(new Set())

    const START_HOUR = 6  
    const END_HOUR = 21 
    const DAYS_AHEAD = 7

    useEffect(() => {
        fetchCurrentUser()
    }, [])

    useEffect(() => {
        if (currentUser?.id) {
            fetchBookedSlots()
        }
    }, [currentUser])

    const fetchCurrentUser = async () => {
        try {
            const response = await axios.get('/users/me')
            setCurrentUser(response.data)
        } catch (error) {
            console.error("Error fetching user:", error)
        }
    }

    const fetchBookedSlots = async () => {
        try {
            const response = await axios.get(`/availability/${currentUser?.id}`)
            const bookings = response.data
            console.log("booking", bookings);
            
            const booked = new Set<string>()
            if (Array.isArray(bookings)) {
                bookings.forEach((booking: any) => {
                    if (booking.status !== 'cancelled') {
                        const hour = parseInt(booking.start_time.split(':')[0])
                        const key = cellKey(booking.booking_date, hour)
                        booked.add(key)
                    }
                })
            }
            
            setBookedSlots(booked)
        } catch (error) {
            console.error("Error fetching booked slots:", error)
        }
    }

    // Generate next 7 days starting today
    const getDates = (): string[] => {
        const dates: string[] = []
        const today = new Date()
        for (let i = 0; i < DAYS_AHEAD; i++) {
            const d = new Date(today)
            d.setDate(today.getDate() + i)
            dates.push(d.toISOString().split('T')[0])
        }
        return dates
    }

    const getHours = (): number[] => {
        const hours: number[] = []
        for (let h = START_HOUR; h < END_HOUR; h++) {
            hours.push(h)
        }
        return hours
    }

    const cellKey = (date: string, hour: number) => `${date}_${hour}`

    const toggleCell = (date: string, hour: number) => {
        const key = cellKey(date, hour)
        
        // Prevent selecting already booked slots
        if (bookedSlots.has(key)) {
            return
        }
        
        setSelectedCells(prev => {
            const next = new Set(prev)
            if (next.has(key)) {
                next.delete(key)
            } else {
                next.add(key)
            }
            return next
        })
    }

    const formatHourLabel = (hour: number): string => {
        const period = hour >= 12 ? 'PM' : 'AM'
        const displayHour = hour % 12 === 0 ? 12 : hour % 12
        return `${displayHour}:00 ${period}`
    }

    const formatDateLabel = (dateStr: string): string => {
        const d = new Date(dateStr + 'T00:00:00')
        return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    }

    const handleSubmit = async () => {
        if (!currentUser?.id) {
            alert('User not logged in')
            return
        }

        if (selectedCells.size === 0) {
            alert('Please select at least one time slot')
            return
        }

        setLoading(true)
        let successCount = 0
        let failCount = 0

        try {
            for (const key of selectedCells) {
                const [date, hourStr] = key.split('_')
                const hour = parseInt(hourStr)
                const startTime = `${String(hour).padStart(2, '0')}:00:00`
                const endTime = `${String(hour + 1).padStart(2, '0')}:00:00`

                try {
                    await axios.post('/availability/', {
                        trainer_id: currentUser.id,
                        booking_date: date,
                        start_time: startTime,
                        end_time: endTime,
                    })
                    successCount++
                } catch (error: any) {
                    console.error(`Failed for ${key}:`, error.response?.data)
                    failCount++
                }
            }

            if (failCount === 0) {
                alert(`Successfully added ${successCount} slot(s)!`)
                setSelectedCells(new Set())
                fetchBookedSlots()
            } else {
                alert(`Added ${successCount} slot(s), ${failCount} failed (check console for details)`)
            }
        } finally {
            setLoading(false)
        }
    }

    const dates = getDates()
    const hours = getHours()

    return (
        <>
            <Navbar />
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-4">
                <div className="max-w-6xl mx-auto bg-white/10 backdrop-blur-md rounded-2xl p-6 shadow-2xl border border-white/20">
                    <h1 className="text-3xl font-bold text-white mb-2 text-center">Set Your Availability</h1>
                    <p className="text-blue-200 text-center mb-6">Click cells to select 1-hour slots (up to 7 days ahead)</p>

                    <div className="overflow-x-auto">
                        <table className="w-full border-collapse">
                            <thead>
                                <tr>
                                    <th className="p-2 text-blue-200 text-sm font-medium sticky left-0 bg-blue-900/80">Time</th>
                                    {dates.map(date => (
                                        <th key={date} className="p-2 text-white text-sm font-medium text-center min-w-[100px]">
                                            {formatDateLabel(date)}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {hours.map(hour => (
                                    <tr key={hour}>
                                        <td className="p-2 text-blue-200 text-sm sticky left-0 bg-blue-900/80 whitespace-nowrap">
                                            {formatHourLabel(hour)}
                                        </td>
                                        {dates.map(date => {
                                            const key = cellKey(date, hour)
                                            const isSelected = selectedCells.has(key)
                                            const isBooked = bookedSlots.has(key)
                                            return (
                                                <td
                                                    key={key}
                                                    onClick={() => toggleCell(date, hour)}
                                                    className={`p-3 border border-white/10 text-center transition-all duration-150 ${
                                                        isBooked
                                                            ? 'bg-red-500/50 cursor-not-allowed opacity-60'
                                                            : isSelected
                                                            ? 'bg-blue-500 hover:bg-blue-400 cursor-pointer'
                                                            : 'bg-white/5 hover:bg-white/15 cursor-pointer'
                                                    }`}
                                                >
                                                    {isSelected && !isBooked && (
                                                        <span className="text-white text-xs font-bold">✓</span>
                                                    )}
                                                    {isBooked && (
                                                        <span className="text-white text-xs font-bold">Booked</span>
                                                    )}
                                                </td>
                                            )
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="mt-6 flex items-center justify-between">
                        <span className="text-blue-200 text-sm">
                            {selectedCells.size} slot(s) selected
                        </span>
                        <button
                            onClick={handleSubmit}
                            disabled={loading || selectedCells.size === 0}
                            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Saving...' : `Save ${selectedCells.size} Slot(s)`}
                        </button>
                    </div>
                </div>
            </section>
        </>
    )
}