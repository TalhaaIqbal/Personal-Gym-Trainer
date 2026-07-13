'use client'

import Link from "next/link"

export default function Hero({ user }: { user: any }) { 

  return (
    <>
      <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex flex-col items-center justify-center p-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Welcome to GymTime
          </h1>
          <p className="text-xl md:text-2xl text-blue-200 mb-8">
            Your Personal Fitness Journey Starts Here
          </p>

          {user ? (
            <div className="space-y-4">
              <p className="text-white text-lg">
                Logged in as: <span className="font-bold">{user.email}</span>
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
                {user.role === 'client' && (
                  <>
                    <Link
                      href="/book-session"
                      className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg"
                    >
                      Book a Session
                    </Link>
                    <Link
                      href="/my-bookings/client"
                      className="px-8 py-4 bg-white/10 backdrop-blur-md text-white font-semibold rounded-lg hover:bg-white/20 transition-all duration-300 border border-white/20"
                    >
                      My Bookings
                    </Link>
                  </>
                )}
                {user.role === 'trainer' && (
                  <>
                    <Link
                      href="/trainer_availability"
                      className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg"
                    >
                      Set Availability
                    </Link>
                    <Link
                      href="/my-bookings/trainer"
                      className="px-8 py-4 bg-white/10 backdrop-blur-md text-white font-semibold rounded-lg hover:bg-white/20 transition-all duration-300 border border-white/20"
                    >
                      My Bookings
                    </Link>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-blue-200 text-lg mb-8">
                Join thousands of clients achieving their fitness goals
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/login"
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="px-8 py-4 bg-white/10 backdrop-blur-md text-white font-semibold rounded-lg hover:bg-white/20 transition-all duration-300 border border-white/20"
                >
                  Sign Up
                </Link>
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  )
}