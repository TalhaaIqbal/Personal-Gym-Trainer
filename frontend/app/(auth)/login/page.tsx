'use client'

import { useState } from 'react'
import Link from 'next/link'
import axios from '@/lib/axios'
import { useRouter } from 'next/navigation'

export default function Login() {
    const router = useRouter()
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        rememberMe: false
    })
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const response = await axios.post('/auth/login', {
                email: formData.email,
                password: formData.password
            })
            
            localStorage.setItem('token', response.data.access_token)
            localStorage.setItem('refreshToken', response.data.refresh_token)
            
            router.push('/')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <>
            <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
                <div className="w-full max-w-md">
                    <div className="bg-gray-500/10 backdrop-blur-md border border-blue-700/50 rounded-2xl shadow-2xl p-8">
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
                            <p className="text-blue-200">Sign in to continue your fitness journey</p>
                        </div>

                        {error && (
                            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-blue-100 mb-2">
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    id="email"
                                    required
                                    className="w-full px-4 py-3 bg-blue-800/50 border border-blue-600/50 rounded-lg text-white placeholder-blue-300/50 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300"
                                    placeholder="Enter your email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>

                            <div>
                                <label htmlFor="password" className="block text-sm font-medium text-blue-100 mb-2">
                                    Password
                                </label>
                                <input
                                    type="password"
                                    id="password"
                                    required
                                    className="w-full px-4 py-3 bg-blue-800/50 border border-blue-600/50 rounded-lg text-white placeholder-blue-300/50 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300"
                                    placeholder="Enter your password"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                />
                            </div>

                            <div className="flex items-center justify-between">
                                <label className="flex items-center">
                                    <input
                                        type="checkbox"
                                        className="w-4 h-4 rounded border-blue-600/50 bg-blue-800/50 text-blue-600 focus:ring-blue-500/50 focus:ring-offset-blue-900"
                                        checked={formData.rememberMe}
                                        onChange={(e) => setFormData({ ...formData, rememberMe: e.target.checked })}
                                    />
                                    <span className="ml-2 text-sm text-blue-200">Remember me</span>
                                </label>
                                <Link href="/forgot-password" className="text-sm text-blue-300 hover:text-white transition-colors duration-300">
                                    Forgot password?
                                </Link>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                            >
                                {loading ? 'Signing in...' : 'Sign In'}
                            </button>
                        </form>

                        <div className="mt-6 text-center">
                            <p className="text-blue-200">
                                Don't have an account?{' '}
                                <Link href="/register" className="text-blue-300 hover:text-white font-medium transition-colors duration-300">
                                    Sign up
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </>
    )
}