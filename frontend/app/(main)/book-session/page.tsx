// 'use client'

// import { useEffect, useState } from 'react'
// import Link from 'next/link'
// import axios from '@/lib/axios'
// import { useRouter } from 'next/navigation'

// interface Availability {
//     id: string
//     trainer_id: string
//     date: string
//     start_time: string
//     end_time: string
//     is_available: boolean
// }

// interface Trainer {
//     id: string
//     name: string
//     email: string
//     role: string
// }

// export default function TrainerAvailability() {
//     const router = useRouter()
//     const [trainers, setTrainers] = useState<Trainer[]>([])
//     const [selectedTrainer, setSelectedTrainer] = useState<string>('')
//     const [availability, setAvailability] = useState<Availability | null>(null)
//     const [loading, setLoading] = useState(false)
//     const [bookingDate, setBookingDate] = useState('')
//     const [bookingStartTime, setBookingStartTime] = useState('')
//     const [bookingEndTime, setBookingEndTime] = useState('')
//     const [currentUser, setCurrentUser] = useState<any>(null)

  
//     return (
//         <>
//             <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
//                 <div className="max-w-4xl w-full bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20">
//                     <h1 className="text-3xl font-bold text-white mb-6 text-center">Book a Training Session</h1>

//                     {/* Trainer Selection */}
//                     <div className="mb-6 items-center flex flex-col space-y-3">
//                         <label className="block text-white font-medium">Select Trainer</label>
//                         <select
//                             value={selectedTrainer}
//                             onChange={(e) => setSelectedTrainer(e.target.value)}
//                             className="w-full p-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
//                         >
//                             <option value="">Choose a trainer...</option>
//                             {trainers.map((trainer) => (
//                                 <option key={trainer.id} value={trainer.id} className="text-gray-900">
//                                     {trainer.name} ({trainer.email})
//                                 </option>
//                             ))}
//                         </select>
//                         <button
//                             type="button"
//                             className="p-3 cursor-pointer bg-white text-black font-semibold rounded-lg shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-[1.02]"
//                             onClick={() => selectedTrainer && fetchAvailability(selectedTrainer)}
//                         >
//                             Show Availability
//                         </button>
//                     </div>

//                     {/* Display Availability */}
//                     {loading && <p className="text-white text-center">Loading availability...</p>}

//                     {availability && (
//                         <div className="mb-6 p-4 bg-blue-600/30 rounded-lg border border-blue-400/30">
//                             <h2 className="text-xl font-semibold text-white mb-3">Trainer Availability</h2>
//                             <div className="text-white space-y-2">
//                                 <p><strong>Date:</strong> {availability.date}</p>
//                                 <p><strong>Available Time:</strong> {availability.start_time} - {availability.end_time}</p>
//                                 <p><strong>Status:</strong> {availability.is_available ? 'Available' : 'Not Available'}</p>
//                             </div>
//                         </div>
//                     )}

//                     {/* Booking Form */}
//                     {availability && availability.is_available && (
//                         <form onSubmit={handleBooking} className="space-y-4">
//                             <div>
//                                 <label className="block text-white mb-2 font-medium">Booking Date</label>
//                                 <input
//                                     type="date"
//                                     value={bookingDate}
//                                     onChange={(e) => setBookingDate(e.target.value)}
//                                     className="w-full p-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
//                                     required
//                                 />
//                             </div>

//                             <div>
//                                 <label className="block text-white mb-2 font-medium">Start Time</label>
//                                 <input
//                                     type="time"
//                                     value={bookingStartTime}
//                                     onChange={(e) => setBookingStartTime(e.target.value)}
//                                     className="w-full p-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
//                                     required
//                                 />
//                             </div>

//                             <div>
//                                 <label className="block text-white mb-2 font-medium">End Time</label>
//                                 <input
//                                     type="time"
//                                     value={bookingEndTime}
//                                     onChange={(e) => setBookingEndTime(e.target.value)}
//                                     className="w-full p-3 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
//                                     required
//                                 />
//                             </div>

//                             <button
//                                 type="submit"
//                                 className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg"
//                             >
//                                 Book Session
//                             </button>
//                         </form>
//                     )}

//                     {!availability && selectedTrainer && !loading && (
//                         <p className="text-white text-center">No availability set for this trainer</p>
//                     )}

//                     <div className="mt-6 text-center">
//                         <Link href="/my-bookings" className="text-blue-300 hover:text-blue-200 underline">
//                             View My Bookings
//                         </Link>
//                     </div>
//                 </div>
//             </section>
//         </>
//     )
// }
