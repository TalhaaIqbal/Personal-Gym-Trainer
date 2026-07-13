'use client'

import { Suspense } from 'react'
import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import axios from '@/lib/axios'

interface Exercise {
    name: string
    muscle_groups: string[]
    sets: number
    reps: string
    weight?: string
    duration?: string
    rest_time?: string
    notes?: string
    video_key?: string
}

interface WorkoutDay {
    date: string
    is_rest_day: boolean
    exercises: Exercise[]
}

interface WorkoutPlan {
    id: string
    trainer_id: string
    client_id: string
    name: string
    description?: string
    days: WorkoutDay[]
    start_date: string
    end_date?: string
    status: string
}

function MyWorkoutPlansContent() {
    const router = useRouter();
    const searchParams = useSearchParams()
    const trainerId = searchParams.get('trainer_id')
    const [plans, setPlans] = useState<WorkoutPlan[]>([])
    const [loading, setLoading] = useState(true)
    const [expandedPlan, setExpandedPlan] = useState<string | null>(null)
    const [videoUrls, setVideoUrls] = useState<Record<string, string>>({})
    const [expandedVideo, setExpandedVideo] = useState<string | null>(null)

    useEffect(() => {
        fetchPlans()
    }, [trainerId])

    const fetchPlans = async () => {
        try {
            const url = trainerId
                ? `/workout-plans/client?trainer_id=${trainerId}`
                : '/workout-plans/client'
            const response = await axios.get(url)
            setPlans(response.data)
        } catch (error) {
            console.error('Error fetching workout plans:', error)
        } finally {
            setLoading(false)
        }
    }

    const fetchVideoUrl = async (videoKey: string) => {
        if (videoUrls[videoKey]) {
            return videoUrls[videoKey]
        }

        try {
            const response = await axios.get(`/videos/workout-video/${videoKey}`)
            const url = response.data.url
            setVideoUrls(prev => ({ ...prev, [videoKey]: url }))
            return url
        } catch (error) {
            console.error('Error fetching video URL:', error)
            return null
        }
    }

    const handleWatchVideo = async (videoKey: string) => {
        if (expandedVideo === videoKey) {
            setExpandedVideo(null)
        } else {
            await fetchVideoUrl(videoKey)
            setExpandedVideo(videoKey)
        }
    }

    if (loading) {
        return (
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center">
                <p className="text-white text-xl">Loading...</p>
            </section>
        )
    }

    return (
        <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-4">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-white mb-6">My Workout Plans</h1>

                {plans.length === 0 ? (
                    <p className="text-white">No workout plans assigned yet.</p>
                ) : (
                    <div className="space-y-6">
                        {plans.map(plan => (
                            <div key={plan.id} className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                                <div className="flex items-center justify-between mb-2">
                                    <div>
                                        <h2 className="text-2xl font-bold text-white">{plan.name}</h2>
                                        {plan.description && (
                                            <p className="text-blue-200 mt-1">{plan.description}</p>
                                        )}
                                    </div>
                                </div>

                                <div className="flex items-center justify-between">
                                    <div className="text-blue-200 text-sm mb-4">
                                        <p>Start Date: {plan.start_date}</p>
                                        {plan.end_date && <p>End Date: {plan.end_date}</p>}
                                        <p>Status: {plan.status}</p>
                                    </div>
                                    <div className="flex flex-col space-y-2">
                                        <button
                                            onClick={() => setExpandedPlan(expandedPlan === plan.id ? null : plan.id)}
                                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                        >
                                            {expandedPlan === plan.id ? 'Hide Details' : 'Show Details'}
                                        </button>
                                        <button
                                            onClick={() => router.push(`/my-bookings/client/workout-plans/${plan.id}`)}
                                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                                        >
                                            Start Workout
                                        </button>
                                    </div>
                                </div>



                                {expandedPlan === plan.id && (
                                    <div className="mt-4 space-y-3">
                                        {plan.days.map((day, dayIndex) => (
                                            <div key={dayIndex} className="bg-white/5 rounded-lg p-4 border border-white/10">
                                                <div className="flex items-center justify-between mb-3">
                                                    <h3 className="text-white font-medium">
                                                        {day.date} {day.is_rest_day && '(Rest Day)'}
                                                    </h3>
                                                    {day.is_rest_day && (
                                                        <span className="px-2 py-1 bg-yellow-600 text-white rounded text-xs">Rest</span>
                                                    )}
                                                </div>

                                                {!day.is_rest_day && day.exercises.length > 0 && (
                                                    <div className="space-y-2">
                                                        {day.exercises.map((exercise, exerciseIndex) => (
                                                            <div key={exerciseIndex} className="bg-white/5 rounded-lg p-3">
                                                                <div className="flex items-center justify-between mb-2">
                                                                    <span className="text-white font-medium">{exercise.name}</span>
                                                                    <span className="text-blue-300 text-sm">
                                                                        {exercise.sets} × {exercise.reps}
                                                                    </span>
                                                                </div>
                                                                {exercise.muscle_groups.length > 0 && (
                                                                    <div className="flex flex-wrap gap-1 mb-2">
                                                                        {exercise.muscle_groups.map((group, gIndex) => (
                                                                            <span key={gIndex} className="px-2 py-1 bg-blue-600 text-white rounded text-xs capitalize">
                                                                                {group}
                                                                            </span>
                                                                        ))}
                                                                    </div>
                                                                )}
                                                                {(exercise.weight || exercise.duration || exercise.rest_time) && (
                                                                    <div className="text-blue-200 text-xs space-x-2">
                                                                        {exercise.weight && <span>Weight: {exercise.weight}</span>}
                                                                        {exercise.duration && <span>Duration: {exercise.duration}</span>}
                                                                        {exercise.rest_time && <span>Rest: {exercise.rest_time}</span>}
                                                                    </div>
                                                                )}
                                                                {exercise.notes && (
                                                                    <p className="text-blue-300 text-xs mt-2 italic">{exercise.notes}</p>
                                                                )}
                                                                {exercise.video_key && (
                                                                    <>
                                                                        <button
                                                                            onClick={() => handleWatchVideo(exercise.video_key!)}
                                                                            className="mt-2 px-3 py-1 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-xs"
                                                                        >
                                                                            {expandedVideo === exercise.video_key ? 'Hide Video' : 'Watch Video'}
                                                                        </button>
                                                                        {expandedVideo === exercise.video_key && videoUrls[exercise.video_key] && (
                                                                            <div className="mt-3">
                                                                                <video
                                                                                    controls
                                                                                    className="w-full rounded-lg"
                                                                                    style={{ maxHeight: '300px' }}
                                                                                >
                                                                                    <source src={videoUrls[exercise.video_key]} type="video/mp4" />
                                                                                    Your browser does not support the video tag.
                                                                                </video>
                                                                            </div>
                                                                        )}
                                                                    </>
                                                                )}
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}

                                                {!day.is_rest_day && day.exercises.length === 0 && (
                                                    <p className="text-blue-300 text-sm italic">No exercises scheduled</p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </section>
    )
}

export default function MyWorkoutPlans() {
    return (
        <Suspense fallback={
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center">
                <p className="text-white text-xl">Loading...</p>
            </section>
        }>
            <MyWorkoutPlansContent />
        </Suspense>
    )
}