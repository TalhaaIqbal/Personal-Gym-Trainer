// 'use client'

// import { useEffect, useState } from 'react'
// import axios from '@/lib/axios'

// interface Booking {
//     id: string
//     trainer_id: string
//     client_id: string
//     booking_date: string
//     start_time: string
//     end_time: string
//     status: 'pending' | 'confirmed' | 'cancelled'
// }

// interface Client {
//     id: string
//     name: string
//     email: string
// }

// export default function TrainerBookings() {
//     const [bookings, setBookings] = useState<Booking[]>([])
//     const [clients, setClients] = useState<Record<string, Client>>({})
//     const [loading, setLoading] = useState(true)
//     const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])

//     useEffect(() => {
//         fetchBookings()
//     }, [])

//     const fetchBookings = async () => {
//         try {
//             const response = await axios.get('/bookings/trainer')
//             setBookings(response.data)
            
//             const clientIds = [...new Set(response.data.map((b: Booking) => b.client_id))]
//             const clientData: Record<string, Client> = {}
            
//             for (const clientId of clientIds) {
//                 try {
//                     const clientResponse = await axios.get(`/users/${clientId}`)
//                     clientData[clientId] = clientResponse.data
//                 } catch (error) {
//                     console.error(`Error fetching client ${clientId}:`, error)
//                 }
//             }
            
//             setClients(clientData)
//         } catch (error) {
//             console.error('Error fetching bookings:', error)
//         } finally {
//             setLoading(false)
//         }
//     }

//     const handleConfirmBooking = async (bookingId: string) => {
//         try {
//             await axios.put(`/bookings/${bookingId}`, { status: 'confirmed' })
//             fetchBookings()
//         } catch (error) {
//             console.error('Error confirming booking:', error)
//             alert('Failed to confirm booking')
//         }
//     }

//     const handleCancelBooking = async (bookingId: string) => {
//         if (!confirm('Are you sure you want to cancel this booking?')) return
        
//         try {
//             await axios.put(`/bookings/${bookingId}`, { status: 'cancelled' })
//             fetchBookings()
//         } catch (error) {
//             console.error('Error cancelling booking:', error)
//             alert('Failed to cancel booking')
//         }
//     }

//     const generateTimeSlots = () => {
//         const slots = []
//         for (let hour = 6; hour <= 20; hour++) {
//             slots.push(`${hour.toString().padStart(2, '0')}:00`)
//         }
//         return slots
//     }

//     const getBookingForSlot = (date: string, time: string) => {
//         return bookings.find(booking => 
//             booking.booking_date === date && 
//             booking.start_time === time &&
//             booking.status !== 'cancelled'
//         )
//     }

//     const getStatusColor = (status: string) => {
//         switch (status) {
//             case 'confirmed': return 'bg-green-500'
//             case 'cancelled': return 'bg-red-500'
//             case 'pending': return 'bg-yellow-500'
//             default: return 'bg-gray-500'
//         }
//     }

//     const getWeekDates = () => {
//         const dates = []
//         const today = new Date(selectedDate)
//         const startOfWeek = new Date(today)
//         startOfWeek.setDate(today.getDate() - today.getDay())
        
//         for (let i = 0; i < 7; i++) {
//             const date = new Date(startOfWeek)
//             date.setDate(startOfWeek.getDate() + i)
//             dates.push(date.toISOString().split('T')[0])
//         }
//         return dates
//     }

//     const weekDates = getWeekDates()
//     const timeSlots = generateTimeSlots()

//     if (loading) {
//         return (
//             <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
//                 <p className="text-white text-xl">Loading bookings...</p>
//             </section>
//         )
//     }

//     return (
//         <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-4">
//             <div className="max-w-7xl mx-auto">
//                 <div className="flex justify-between items-center mb-6">
//                     <h1 className="text-3xl font-bold text-white">Your Bookings</h1>
//                     <input
//                         type="date"
//                         value={selectedDate}
//                         onChange={(e) => setSelectedDate(e.target.value)}
//                         className="p-2 rounded-lg bg-white/20 text-white border border-white/30"
//                     />
//                 </div>

//                 <div className="bg-white/10 backdrop-blur-md rounded-xl overflow-hidden border border-white/20">
//                     <div className="grid grid-cols-8 bg-white/20">
//                         <div className="p-3 text-white font-semibold border-r border-white/30">Time</div>
//                         {weekDates.map(date => (
//                             <div key={date} className="p-3 text-white font-semibold text-center border-r border-white/30">
//                                 {new Date(date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
//                             </div>
//                         ))}
//                     </div>

//                     {timeSlots.map(time => (
//                         <div key={time} className="grid grid-cols-8 border-t border-white/20">
//                             <div className="p-3 text-white border-r border-white/30 text-sm">
//                                 {time}
//                             </div>
//                             {weekDates.map(date => {
//                                 const booking = getBookingForSlot(date, time)
//                                 const client = booking ? clients[booking.client_id] : null
                                
//                                 return (
//                                     <div
//                                         key={`${date}-${time}`}
//                                         className={`p-3 border-r border-white/30 min-h-[60px] ${
//                                             booking ? getStatusColor(booking.status) : 'bg-white/5'
//                                         }`}
//                                     >
//                                         {booking && client && (
//                                             <div className="text-xs text-white">
//                                                 <div className="font-semibold truncate">{client.name}</div>
//                                                 <div className="truncate">{booking.status}</div>
//                                             </div>
//                                         )}
//                                     </div>
//                                 )
//                             })}
//                         </div>
//                     ))}
//                 </div>

//                 <div className="mt-6 bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
//                     <h2 className="text-xl font-bold text-white mb-4">Booking Details</h2>
//                     {bookings.length === 0 ? (
//                         <p className="text-white">No bookings yet</p>
//                     ) : (
//                         <div className="space-y-3">
//                             {bookings.filter(b => b.status !== 'cancelled').map(booking => {
//                                 const client = clients[booking.client_id]
//                                 return (
//                                     <div key={booking.id} className="flex items-center justify-between p-4 bg-white/10 rounded-lg">
//                                         <div>
//                                             <p className="text-white font-semibold">
//                                                 {client?.name || 'Unknown Client'}
//                                             </p>
//                                             <p className="text-blue-200 text-sm">
//                                                 {booking.booking_date} | {booking.start_time} - {booking.end_time}
//                                             </p>
//                                             <p className="text-blue-200 text-sm">
//                                                 {client?.email || ''}
//                                             </p>
//                                         </div>
//                                         <div className="flex gap-2">
//                                             {booking.status === 'pending' && (
//                                                 <button
//                                                     onClick={() => handleConfirmBooking(booking.id)}
//                                                     className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
//                                                 >
//                                                     Confirm
//                                                 </button>
//                                             )}
//                                             <button
//                                                 onClick={() => handleCancelBooking(booking.id)}
//                                                 className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
//                                             >
//                                                 Cancel
//                                             </button>
//                                         </div>
//                                     </div>
//                                 )
//                             })}
//                         </div>
//                     )}
//                 </div>
//             </div>
//         </section>
//     )
// }
