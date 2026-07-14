'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import Navbar from '../../../../../components/navbar'
import axios from '@/lib/axios'
import process from 'process'
import { DNA } from 'react-loader-spinner'

interface Exercise {
    name: string
    sets: number
    reps: number
    muscle_groups: string[]
    weight?: string
    duration?: string
    rest_time?: string
    notes?: string
    video_key?: string
}

interface Day {
    date: string
    is_rest_day: boolean
    exercises: Exercise[]
}

interface WorkoutPlan {
    id: string
    name: string
    description?: string
    start_date: string
    end_date?: string
    status: string
    days: Day[]
}

interface ProgressEntry {
    id: string
    date: string
    weightKg: number | null
    notes: string
    workoutCompleted: boolean
    createdAt: number
    dayIndex?: number
}

const STORAGE_KEY = process.env.NEXT_PUBLIC_PROGRESS_LOG_KEY || 'gym_progress_log_key'
const MAX_HISTORY = 50

export default function ProgressLogger() {
    const params = useParams()
    const planId = params.id as string

    const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null)
    const [loadingPlan, setLoadingPlan] = useState(true)
    const [entries, setEntries] = useState<ProgressEntry[]>([])
    const [history, setHistory] = useState<ProgressEntry[][]>([])
    const [historyIndex, setHistoryIndex] = useState(-1)
    const [selectedDayIndex, setSelectedDayIndex] = useState<number | null>(null)
    const [videoUrls, setVideoUrls] = useState<Record<string, string>>({})

    const [weight, setWeight] = useState('')
    const [notes, setNotes] = useState('')
    const [workoutCompleted, setWorkoutCompleted] = useState(false)

    useEffect(() => {
        const fetchWorkoutPlan = async () => {
            try {
                const response = await axios.get(`/workout-plans/${planId}`)
                setWorkoutPlan(response.data)
                setLoadingPlan(false)
            } catch (error) {
                console.error('Failed to fetch workout plan:', error)
                setLoadingPlan(false)
            }
        }

        const loadProgressEntries = () => {
            try {
                const stored = localStorage.getItem(STORAGE_KEY)
                if (stored) {
                    const parsed: ProgressEntry[] = JSON.parse(stored)
                    const planEntries = parsed.filter(entry => entry.dayIndex !== undefined)
                    setEntries(planEntries)
                    setHistory([planEntries])
                    setHistoryIndex(0)
                } else {
                    setHistory([[]])
                    setHistoryIndex(0)
                }
            } catch (error) {
                console.error('Failed to load progress log:', error)
                setHistory([[]])
                setHistoryIndex(0)
            }
        }

        fetchWorkoutPlan()
        loadProgressEntries()
    }, [planId])

    useEffect(() => {
        if (historyIndex >= 0) {
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(entries))
            } catch (error) {
                console.error('Failed to save progress log:', error)
            }
        }
    }, [entries])

    const commitChange = (newEntries: ProgressEntry[]) => {
        const truncatedHistory = history.slice(0, historyIndex + 1)
        const updatedHistory = [...truncatedHistory, newEntries].slice(-MAX_HISTORY)
        setHistory(updatedHistory)
        setHistoryIndex(updatedHistory.length - 1)
        setEntries(newEntries)
    }

    const handleAddEntry = () => {
        if (selectedDayIndex === null) {
            alert('Please select a workout day first')
            return
        }
        if (!weight && !notes && !workoutCompleted) {
            alert('Please fill in at least one field')
            return
        }

        const newEntry: ProgressEntry = {
            id: crypto.randomUUID(),
            date: new Date().toISOString().split('T')[0],
            weightKg: weight ? parseFloat(weight) : null,
            notes,
            workoutCompleted,
            createdAt: Date.now(),
            dayIndex: selectedDayIndex,
        }

        commitChange([newEntry, ...entries])

        setWeight('')
        setNotes('')
        setWorkoutCompleted(false)
    }

    const handleDeleteEntry = (id: string) => {
        commitChange(entries.filter(e => e.id !== id))
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
        const url = await fetchVideoUrl(videoKey)
        if (url) {
            window.open(url, '_blank')
        }
    }

    const handleUndo = useCallback(() => {
        if (historyIndex > 0) {
            const newIndex = historyIndex - 1
            setHistoryIndex(newIndex)
            setEntries(history[newIndex])
        }
    }, [historyIndex, history])

    const handleRedo = useCallback(() => {
        if (historyIndex < history.length - 1) {
            const newIndex = historyIndex + 1
            setHistoryIndex(newIndex)
            setEntries(history[newIndex])
        }
    }, [historyIndex, history])

    const canUndo = historyIndex > 0
    const canRedo = historyIndex < history.length - 1

    return (
        <>
            <Navbar />
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-4">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-between mb-6">
                        <h1 className="text-3xl font-bold text-white">
                            {loadingPlan ? <DNA visible={true} height="40" width="40" ariaLabel="dna-loading" wrapperStyle={{}} wrapperClass="dna-wrapper" /> : workoutPlan?.name || 'Workout Plan'}
                        </h1>
                        <div className="flex gap-2">
                            <button
                                onClick={handleUndo}
                                disabled={!canUndo}
                                className="px-3 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed text-sm"
                            >
                                ↩ Undo
                            </button>
                            <button
                                onClick={handleRedo}
                                disabled={!canRedo}
                                className="px-3 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed text-sm"
                            >
                                ↪ Redo
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Workout Plan Section */}
                        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                            <h2 className="text-xl font-semibold text-white mb-4">Workout Plan</h2>
                            {loadingPlan ? (
                                <DNA visible={true} height="80" width="80" ariaLabel="dna-loading" wrapperStyle={{}} wrapperClass="dna-wrapper" />
                            ) : workoutPlan ? (
                                <>
                                    {workoutPlan.description && (
                                        <p className="text-blue-200 mb-4">{workoutPlan.description}</p>
                                    )}
                                    <div className="text-blue-200 text-sm mb-4">
                                        <p>Start Date: {workoutPlan.start_date}</p>
                                        {workoutPlan.end_date && <p>End Date: {workoutPlan.end_date}</p>}
                                        <p>Status: {workoutPlan.status}</p>
                                    </div>

                                    <div className="space-y-3">
                                        {workoutPlan.days.map((day, dayIndex) => (
                                            <div
                                                key={dayIndex}
                                                className={`bg-white/5 rounded-lg p-4 border border-white/10 cursor-pointer transition-all ${
                                                    selectedDayIndex === dayIndex ? 'ring-2 ring-blue-500' : ''
                                                }`}
                                                onClick={() => setSelectedDayIndex(dayIndex)}
                                            >
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
                                                                    <button
                                                                        onClick={() => handleWatchVideo(exercise.video_key!)}
                                                                        className="mt-2 px-3 py-1 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-xs"
                                                                    >
                                                                        Watch Video
                                                                    </button>
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
                                </>
                            ) : (
                                <p className="text-red-200">Failed to load workout plan</p>
                            )}
                        </div>

                        {/* Progress Log Section */}
                        <div className="space-y-6">
                            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                                <h2 className="text-lg font-semibold text-white mb-3">
                                    Log Progress for {selectedDayIndex !== null ? workoutPlan?.days[selectedDayIndex]?.date : 'Selected Day'}
                                </h2>
                                <input
                                    type="number"
                                    placeholder="Weight (kg)"
                                    value={weight}
                                    onChange={(e) => setWeight(e.target.value)}
                                    className="w-full p-3 mb-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                <textarea
                                    placeholder="How did it feel?"
                                    value={notes}
                                    onChange={(e) => setNotes(e.target.value)}
                                    className="w-full p-3 mb-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    rows={3}
                                />
                                <label className="flex items-center gap-2 text-white mb-4 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={workoutCompleted}
                                        onChange={(e) => setWorkoutCompleted(e.target.checked)}
                                        className="w-4 h-4"
                                    />
                                    Workout completed today
                                </label>
                                <button
                                    onClick={handleAddEntry}
                                    className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700"
                                >
                                    Save Entry
                                </button>
                            </div>

                            {/* History */}
                            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                                <h2 className="text-xl font-semibold text-white mb-3">Progress History</h2>
                                {entries.length === 0 ? (
                                    <p className="text-blue-200">No entries yet.</p>
                                ) : (
                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                        {entries.map(entry => (
                                            <div key={entry.id} className="bg-white/5 rounded-xl p-4 border border-white/10 flex justify-between items-start">
                                                <div>
                                                    <p className="text-white font-medium">
                                                        {entry.date} - {entry.dayIndex !== undefined && workoutPlan ? workoutPlan.days[entry.dayIndex]?.date : ''}
                                                    </p>
                                                    {entry.weightKg !== null && (
                                                        <p className="text-blue-200 text-sm">Weight: {entry.weightKg} kg</p>
                                                    )}
                                                    {entry.notes && (
                                                        <p className="text-blue-200 text-sm">{entry.notes}</p>
                                                    )}
                                                    {entry.workoutCompleted && (
                                                        <span className="inline-block mt-1 px-2 py-1 bg-green-600/50 text-white text-xs rounded-full">
                                                            ✓ Workout completed
                                                        </span>
                                                    )}
                                                </div>
                                                <button
                                                    onClick={() => handleDeleteEntry(entry.id)}
                                                    className="px-3 py-1 bg-red-600/50 text-white rounded-lg hover:bg-red-600/70 text-sm"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </>
    )
}