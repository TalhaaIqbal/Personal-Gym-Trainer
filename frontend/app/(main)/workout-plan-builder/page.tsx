'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import axios from '@/lib/axios'
import Link from 'next/link'

interface Exercise {
    name: string
    sets: number
    reps: string
    weight?: string
    duration?: string
    rest_time?: string
    notes?: string
}

interface Client {
    id: string
    name: string
    email: string
}

export default function WorkoutPlanBuilder() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [client, setClient] = useState<Client | null>(null)
    const [planName, setPlanName] = useState('')
    const [description, setDescription] = useState('')
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')
    const [exercises, setExercises] = useState<Exercise[]>([
        { name: '', sets: 3, reps: '10-12', weight: '', duration: '', rest_time: '60s', notes: '' }
    ])
    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        const clientId = searchParams.get('client_id')
        if (clientId) {
            fetchClient(clientId)
        } else {
            setLoading(false)
        }
    }, [searchParams])

    const fetchClient = async (clientId: string) => {
        try {
            const response = await axios.get(`/users/${clientId}`)
            setClient(response.data)
        } catch (error) {
            console.error('Error fetching client:', error)
            alert('Failed to load client information')
        } finally {
            setLoading(false)
        }
    }

    const addExercise = () => {
        setExercises([...exercises, { name: '', sets: 3, reps: '10-12', weight: '', duration: '', rest_time: '60s', notes: '' }])
    }

    const removeExercise = (index: number) => {
        if (exercises.length > 1) {
            setExercises(exercises.filter((_, i) => i !== index))
        }
    }

    const updateExercise = (index: number, field: keyof Exercise, value: string | number) => {
        const updatedExercises = [...exercises]
        updatedExercises[index] = { ...updatedExercises[index], [field]: value }
        setExercises(updatedExercises)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        
        if (!client || !planName || !startDate) {
            alert('Please fill in all required fields')
            return
        }

        const validExercises = exercises.filter(ex => ex.name.trim() !== '')
        if (validExercises.length === 0) {
            alert('Please add at least one exercise')
            return
        }

        setSubmitting(true)

        try {
            const workoutPlan = {
                client_id: client.id,
                name: planName,
                description: description || null,
                exercises: validExercises,
                start_date: startDate,
                end_date: endDate || null
            }

            await axios.post('/workout-plans', workoutPlan)
            alert('Workout plan created successfully!')
            router.push('/my-bookings/trainer')
        } catch (error: any) {
            console.error('Error creating workout plan:', error)
            alert(error.response?.data?.detail || 'Failed to create workout plan')
        } finally {
            setSubmitting(false)
        }
    }

    if (loading) {
        return (
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
                <p className="text-white text-xl">Loading client information...</p>
            </section>
        )
    }

    if (!client) {
        return (
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
                <div className="text-center">
                    <p className="text-white text-xl mb-4">No client selected</p>
                    <Link href="/my-bookings/trainer" className="text-blue-300 hover:text-blue-200 underline">
                        Go back to dashboard
                    </Link>
                </div>
            </section>
        )
    }

    return (
        <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-4">
            <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-3xl font-bold text-white">Workout Plan Builder</h1>
                    <Link href="/my-bookings/trainer" className="text-blue-300 hover:text-blue-200">
                        ← Back to Dashboard
                    </Link>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Client Information */}
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                        <h2 className="text-xl font-semibold text-white mb-4">Client</h2>
                        <div className="text-blue-200">
                            <p className="font-semibold text-white text-lg">{client.name}</p>
                            <p className="text-sm">{client.email}</p>
                        </div>
                    </div>

                    {/* Plan Details */}
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                        <h2 className="text-xl font-semibold text-white mb-4">Plan Details</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-blue-200 mb-2">Plan Name *</label>
                                <input
                                    type="text"
                                    value={planName}
                                    onChange={(e) => setPlanName(e.target.value)}
                                    className="w-full px-4 py-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="e.g., Strength Training Program"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-blue-200 mb-2">Description</label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    className="w-full px-4 py-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Brief description of the workout plan..."
                                    rows={3}
                                />
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-blue-200 mb-2">Start Date *</label>
                                    <input
                                        type="date"
                                        value={startDate}
                                        onChange={(e) => setStartDate(e.target.value)}
                                        className="w-full px-4 py-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-blue-200 mb-2">End Date (Optional)</label>
                                    <input
                                        type="date"
                                        value={endDate}
                                        onChange={(e) => setEndDate(e.target.value)}
                                        className="w-full px-4 py-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Exercises */}
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold text-white">Exercises</h2>
                            <button
                                type="button"
                                onClick={addExercise}
                                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                            >
                                + Add Exercise
                            </button>
                        </div>

                        {exercises.map((exercise, index) => (
                            <div key={index} className="bg-white/5 rounded-lg p-4 mb-4 border border-white/10">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-medium text-white">Exercise {index + 1}</h3>
                                    {exercises.length > 1 && (
                                        <button
                                            type="button"
                                            onClick={() => removeExercise(index)}
                                            className="px-3 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                                        >
                                            Remove
                                        </button>
                                    )}
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="md:col-span-2">
                                        <label className="block text-blue-200 mb-2">Exercise Name *</label>
                                        <input
                                            type="text"
                                            value={exercise.name}
                                            onChange={(e) => updateExercise(index, 'name', e.target.value)}
                                            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="e.g., Bench Press"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-blue-200 mb-2">Sets *</label>
                                        <input
                                            type="number"
                                            value={exercise.sets}
                                            onChange={(e) => updateExercise(index, 'sets', parseInt(e.target.value))}
                                            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            min="1"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-blue-200 mb-2">Reps *</label>
                                        <input
                                            type="text"
                                            value={exercise.reps}
                                            onChange={(e) => updateExercise(index, 'reps', e.target.value)}
                                            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="e.g., 10-12"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-blue-200 mb-2">Weight (Optional)</label>
                                        <input
                                            type="text"
                                            value={exercise.weight}
                                            onChange={(e) => updateExercise(index, 'weight', e.target.value)}
                                            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="e.g., 135 lbs"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-blue-200 mb-2">Duration (Optional)</label>
                                        <input
                                            type="text"
                                            value={exercise.duration}
                                            onChange={(e) => updateExercise(index, 'duration', e.target.value)}
                                            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="e.g., 30 min"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-blue-200 mb-2">Rest Time (Optional)</label>
                                        <input
                                            type="text"
                                            value={exercise.rest_time}
                                            onChange={(e) => updateExercise(index, 'rest_time', e.target.value)}
                                            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="e.g., 60s"
                                        />
                                    </div>
                                    <div className="md:col-span-2">
                                        <label className="block text-blue-200 mb-2">Notes (Optional)</label>
                                        <textarea
                                            value={exercise.notes}
                                            onChange={(e) => updateExercise(index, 'notes', e.target.value)}
                                            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="Any additional instructions..."
                                            rows={2}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Submit Button */}
                    <div className="flex justify-end space-x-4">
                        <Link
                            href="/my-bookings/trainer"
                            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                        >
                            Cancel
                        </Link>
                        <button
                            type="submit"
                            disabled={submitting}
                            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {submitting ? 'Creating...' : 'Create Workout Plan'}
                        </button>
                    </div>
                </form>
            </div>
        </section>
    )
}
