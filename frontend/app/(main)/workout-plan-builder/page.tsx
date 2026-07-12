'use client'

import { Suspense } from 'react'
import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import axios from '@/lib/axios'
import Link from 'next/link'

interface Exercise {
    name: string
    muscle_groups: string[]
    sets: number
    reps: string
    weight?: string
    duration?: string
    rest_time?: string
    notes?: string
    video_file?: File
}

interface Client {
    id: string
    name: string
    email: string
}

interface WorkoutDay {
    date: string
    is_rest_day: boolean
    exercises: Exercise[]
}

const MUSCLE_GROUPS = [
    'chest', 'back', 'legs', 'shoulders', 'bicep', 'tricep', 'cardio', 'core', 'mixed'
] as const

function WorkoutPlanBuilderContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [client, setClient] = useState<Client | null>(null)
    const [planName, setPlanName] = useState('')
    const [description, setDescription] = useState('')
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')
    const [workoutDays, setWorkoutDays] = useState<WorkoutDay[]>([
        { date: '', is_rest_day: false, exercises: [{ name: '', muscle_groups: [], sets: 3, reps: '10-12', weight: '', duration: '', rest_time: '60s', notes: '' }] }
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

    const addExercise = (dayIndex: number) => {
        const updatedDays = [...workoutDays]
        updatedDays[dayIndex].exercises.push({ name: '', muscle_groups: [], sets: 3, reps: '10-12', weight: '', duration: '', rest_time: '60s', notes: '' })
        setWorkoutDays(updatedDays)
    }

    const removeExercise = (dayIndex: number, exerciseIndex: number) => {
        const updatedDays = [...workoutDays]
        if (updatedDays[dayIndex].exercises.length > 1) {
            updatedDays[dayIndex].exercises = updatedDays[dayIndex].exercises.filter((_, i) => i !== exerciseIndex)
            setWorkoutDays(updatedDays)
        }
    }

    const updateExercise = (dayIndex: number, exerciseIndex: number, field: keyof Exercise, value: string | number | string[]) => {
        const updatedDays = [...workoutDays]
        updatedDays[dayIndex].exercises[exerciseIndex] = { ...updatedDays[dayIndex].exercises[exerciseIndex], [field]: value }
        setWorkoutDays(updatedDays)
    }

    const handleVideoSelect = (dayIndex: number, exerciseIndex: number, file: File) => {
        const updatedDays = [...workoutDays]
        updatedDays[dayIndex].exercises[exerciseIndex] = { ...updatedDays[dayIndex].exercises[exerciseIndex], video_file: file }
        setWorkoutDays(updatedDays)
    }

    const handleRemoveVideo = (dayIndex: number, exerciseIndex: number) => {
        const updatedDays = [...workoutDays]
        updatedDays[dayIndex].exercises[exerciseIndex] = { ...updatedDays[dayIndex].exercises[exerciseIndex], video_file: undefined }
        setWorkoutDays(updatedDays)
    }

    const uploadVideo = async (file: File): Promise<string> => {
        const formData = new FormData()
        formData.append('file', file)

        const response = await axios.post('/videos/workout-video/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })

        return response.data.video_key
    }

    const toggleMuscleGroup = (dayIndex: number, exerciseIndex: number, muscleGroup: string) => {
        const updatedDays = [...workoutDays]
        const currentGroups = updatedDays[dayIndex].exercises[exerciseIndex].muscle_groups
        if (currentGroups.includes(muscleGroup)) {
            updatedDays[dayIndex].exercises[exerciseIndex].muscle_groups = currentGroups.filter(g => g !== muscleGroup)
        } else {
            updatedDays[dayIndex].exercises[exerciseIndex].muscle_groups = [...currentGroups, muscleGroup]
        }
        setWorkoutDays(updatedDays)
    }

    const toggleRestDay = (dayIndex: number) => {
        const updatedDays = [...workoutDays]
        updatedDays[dayIndex].is_rest_day = !updatedDays[dayIndex].is_rest_day
        setWorkoutDays(updatedDays)
    }

    const updateDayDate = (dayIndex: number, date: string) => {
        const updatedDays = [...workoutDays]
        updatedDays[dayIndex].date = date
        setWorkoutDays(updatedDays)
    }

    const generateWorkoutDays = () => {
        if (!startDate || !endDate) return

        const start = new Date(startDate)
        const end = new Date(endDate)
        const days: WorkoutDay[] = []

        const currentDate = new Date(start)
        while (currentDate <= end) {
            days.push({
                date: currentDate.toISOString().split('T')[0],
                is_rest_day: false,
                exercises: [{ name: '', muscle_groups: [], sets: 3, reps: '10-12', weight: '', duration: '', rest_time: '60s', notes: '' }]
            })
            currentDate.setDate(currentDate.getDate() + 1)
        }

        setWorkoutDays(days)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!client || !planName || !startDate) {
            alert('Please fill in all required fields')
            return
        }

        const validDays = workoutDays.filter(day =>
            day.date && (day.is_rest_day || day.exercises.some(ex => ex.name.trim() !== ''))
        )

        if (validDays.length === 0) {
            alert('Please add at least one workout day with a date')
            return
        }

        const daysWithExercises = validDays.map(day => ({
            ...day,
            exercises: day.is_rest_day ? [] : day.exercises
                .filter(ex => ex.name.trim() !== '')
                .map(ex => ({
                    ...ex,
                    weight: ex.weight || undefined,
                    duration: ex.duration || undefined,
                    notes: ex.notes || undefined,
                    video_file: ex.video_file || undefined
                }))
        }))

        setSubmitting(true)

        try {
            // Upload videos first and get video keys
            const daysWithVideoKeys = await Promise.all(
                daysWithExercises.map(async (day) => ({
                    ...day,
                    exercises: await Promise.all(
                        day.exercises.map(async (exercise) => ({
                            ...exercise,
                            video_key: exercise.video_file ? await uploadVideo(exercise.video_file) : undefined,
                            video_file: undefined
                        }))
                    )
                }))
            )

            const workoutPlan = {
                client_id: client.id,
                name: planName,
                description: description || null,
                days: daysWithVideoKeys,
                start_date: startDate,
                end_date: endDate || null
            }

            console.log('Sending workout plan:', JSON.stringify(workoutPlan, null, 2))

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
                            {startDate && endDate && (
                                <button
                                    type="button"
                                    onClick={generateWorkoutDays}
                                    className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                                >
                                    Generate Workout Days
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Workout Days */}
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold text-white">Workout Days</h2>
                            <span className="text-blue-200 text-sm">
                                {workoutDays.length} day{workoutDays.length !== 1 ? 's' : ''} planned
                            </span>
                        </div>

                        {workoutDays.map((day, dayIndex) => (
                            <div key={dayIndex} className="bg-white/5 rounded-lg p-4 mb-4 border border-white/10">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-4">
                                        <h3 className="text-lg font-medium text-white">Day {dayIndex + 1}</h3>
                                        <input
                                            type="date"
                                            value={day.date}
                                            onChange={(e) => updateDayDate(dayIndex, e.target.value)}
                                            className="px-3 py-1 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                        />
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => toggleRestDay(dayIndex)}
                                        className={`px-3 py-1 rounded-lg text-sm ${day.is_rest_day ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-gray-600 hover:bg-gray-700'} text-white`}
                                    >
                                        {day.is_rest_day ? 'Rest Day' : 'Workout Day'}
                                    </button>
                                </div>

                                {!day.is_rest_day && (
                                    <>
                                        <div className="flex items-center justify-between mb-4">
                                            <h4 className="text-md font-medium text-blue-200">Exercises</h4>
                                            <button
                                                type="button"
                                                onClick={() => addExercise(dayIndex)}
                                                className="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                                            >
                                                + Add Exercise
                                            </button>
                                        </div>

                                        {day.exercises.map((exercise, exerciseIndex) => (
                                            <div key={exerciseIndex} className="bg-white/5 rounded-lg p-4 mb-3 border border-white/10">
                                                <div className="flex items-center justify-between mb-3">
                                                    <h5 className="text-sm font-medium text-white">Exercise {exerciseIndex + 1}</h5>
                                                    {day.exercises.length > 1 && (
                                                        <button
                                                            type="button"
                                                            onClick={() => removeExercise(dayIndex, exerciseIndex)}
                                                            className="px-2 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 text-xs"
                                                        >
                                                            Remove
                                                        </button>
                                                    )}
                                                </div>

                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                    <div className="md:col-span-2">
                                                        <label className="block text-blue-200 mb-1 text-sm">Exercise Name *</label>
                                                        <input
                                                            type="text"
                                                            value={exercise.name}
                                                            onChange={(e) => updateExercise(dayIndex, exerciseIndex, 'name', e.target.value)}
                                                            className="w-full px-3 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                                            placeholder="e.g., Bench Press"
                                                        />
                                                    </div>
                                                    <div className="md:col-span-2">
                                                        <label className="block text-blue-200 mb-1 text-sm">Muscle Groups *</label>
                                                        <div className="flex flex-wrap gap-2">
                                                            {MUSCLE_GROUPS.map((group) => (
                                                                <button
                                                                    key={group}
                                                                    type="button"
                                                                    onClick={() => toggleMuscleGroup(dayIndex, exerciseIndex, group)}
                                                                    className={`px-3 py-1 rounded-lg text-xs capitalize ${exercise.muscle_groups.includes(group)
                                                                            ? 'bg-blue-600 text-white'
                                                                            : 'bg-white/20 text-blue-200 hover:bg-white/30'
                                                                        }`}
                                                                >
                                                                    {group}
                                                                </button>
                                                            ))}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <label className="block text-blue-200 mb-1 text-sm">Sets *</label>
                                                        <input
                                                            type="number"
                                                            value={exercise.sets}
                                                            onChange={(e) => updateExercise(dayIndex, exerciseIndex, 'sets', parseInt(e.target.value))}
                                                            className="w-full px-3 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                                            min="1"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-blue-200 mb-1 text-sm">Reps *</label>
                                                        <input
                                                            type="text"
                                                            value={exercise.reps}
                                                            onChange={(e) => updateExercise(dayIndex, exerciseIndex, 'reps', e.target.value)}
                                                            className="w-full px-3 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                                            placeholder="e.g., 10-12"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-blue-200 mb-1 text-sm">Weight (Optional)</label>
                                                        <input
                                                            type="text"
                                                            value={exercise.weight}
                                                            onChange={(e) => updateExercise(dayIndex, exerciseIndex, 'weight', e.target.value)}
                                                            className="w-full px-3 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                                            placeholder="e.g., 70 kg"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-blue-200 mb-1 text-sm">Duration (Optional)</label>
                                                        <input
                                                            type="text"
                                                            value={exercise.duration}
                                                            onChange={(e) => updateExercise(dayIndex, exerciseIndex, 'duration', e.target.value)}
                                                            className="w-full px-3 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                                            placeholder="e.g., 30 min"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-blue-200 mb-1 text-sm">Rest Time (Optional)</label>
                                                        <input
                                                            type="text"
                                                            value={exercise.rest_time}
                                                            onChange={(e) => updateExercise(dayIndex, exerciseIndex, 'rest_time', e.target.value)}
                                                            className="w-full px-3 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                                            placeholder="e.g., 60s"
                                                        />
                                                    </div>
                                                    <div className="md:col-span-2">
                                                        <label className="block text-blue-200 mb-1 text-sm">Notes (Optional)</label>
                                                        <textarea
                                                            value={exercise.notes}
                                                            onChange={(e) => updateExercise(dayIndex, exerciseIndex, 'notes', e.target.value)}
                                                            className="w-full px-3 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                                            placeholder="Any additional instructions..."
                                                            rows={2}
                                                        />
                                                    </div>
                                                    <div className="md:col-span-2">
                                                        <label className="block text-blue-200 mb-1 text-sm">Exercise Video (Optional)</label>
                                                        {!exercise.video_file ? (
                                                            <div className="flex items-center gap-2">
                                                                <input
                                                                    type="file"
                                                                    accept="video/*"
                                                                    onChange={(e) => {
                                                                        const file = e.target.files?.[0]
                                                                        if (file) handleVideoSelect(dayIndex, exerciseIndex, file)
                                                                    }}
                                                                    className="hidden"
                                                                    id={`video-upload-${dayIndex}-${exerciseIndex}`}
                                                                />
                                                                <label
                                                                    htmlFor={`video-upload-${dayIndex}-${exerciseIndex}`}
                                                                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 cursor-pointer text-sm"
                                                                >
                                                                    Select Video
                                                                </label>
                                                            </div>
                                                        ) : (
                                                            <div className="flex items-center justify-between bg-white/10 rounded-lg p-3">
                                                                <span className="text-green-400 text-sm">✓ {exercise.video_file.name}</span>
                                                                <button
                                                                    type="button"
                                                                    onClick={() => handleRemoveVideo(dayIndex, exerciseIndex)}
                                                                    className="px-3 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 text-xs"
                                                                >
                                                                    Remove
                                                                </button>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </>
                                )}
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

export default function WorkoutPlanBuilder() {
    return (
        <Suspense fallback={
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
                <p className="text-white text-xl">Loading...</p>
            </section>
        }>
            <WorkoutPlanBuilderContent />
        </Suspense>
    )
}
