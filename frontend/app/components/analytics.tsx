'use client'

import React, { useEffect, useState } from 'react'
import axios from '@/lib/axios'
import Navbar from './navbar'
import { DNA } from 'react-loader-spinner'

interface OverviewStats {
  total_clients: number
  total_bookings: number
  confirmed_bookings: number
  pending_bookings: number
  cancelled_bookings: number
  completion_rate: number
  recent_bookings: number
  upcoming_bookings: number
}

interface BookingTrend {
  date: string
  confirmed: number
  pending: number
  cancelled: number
  total: number
}

interface ClientStat {
  client_id: string
  client_name: string
  client_email: string
  total_sessions: number
  completed_sessions: number
  cancelled_sessions: number
  completion_rate: number
  last_session_date: string
}

interface TimeSlot {
  hour: number
  count: number
  time_label: string
}

interface RevenueData {
  month: string
  revenue: number
  sessions: number
}

export default function TrainerAnalytics() {
  const [overview, setOverview] = useState<OverviewStats | null>(null)
  const [bookingTrends, setBookingTrends] = useState<BookingTrend[]>([])
  const [clientStats, setClientStats] = useState<ClientStat[]>([])
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([])
  const [revenueData, setRevenueData] = useState<RevenueData[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchAnalyticsData()
  }, [])

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true)
      const [overviewRes, trendsRes, clientRes, timeRes, revenueRes] = await Promise.all([
        axios.get('/analytics/overview'),
        axios.get('/analytics/booking-trends'),
        axios.get('/analytics/client-stats'),
        axios.get('/analytics/time-slots'),
        axios.get('/analytics/revenue')
      ])

      setOverview(overviewRes.data)
      setBookingTrends(trendsRes.data)
      setClientStats(clientRes.data)
      setTimeSlots(timeRes.data)
      setRevenueData(revenueRes.data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, subtitle, color }: { title: string; value: string | number; subtitle?: string; color: string }) => (
    <div className={`${color} rounded-xl p-4 sm:p-6 shadow-lg`}>
      <h3 className="text-white/80 text-xs sm:text-sm font-medium mb-2">{title}</h3>
      <p className="text-white text-2xl sm:text-3xl font-bold">{value}</p>
      {subtitle && <p className="text-white/60 text-xs mt-1">{subtitle}</p>}
    </div>
  )

  if (loading) {
    return (
      <>
        <Navbar />
        <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
          <DNA visible={true} height="80" width="80" ariaLabel="dna-loading" wrapperStyle={{}} wrapperClass="dna-wrapper" />
        </section>
      </>
    )
  }

  return (
    <>
      <Navbar />
      <section className="pt-20 min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-2">Trainer Analytics</h1>
          <p className="text-blue-200 mb-8">Track your performance and client trends</p>

          {/* Tab Navigation */}
          <div className="flex overflow-x-auto space-x-2 mb-6 bg-white/10 rounded-lg p-1 scrollbar-hide">
            {['overview', 'trends', 'clients', 'time-slots', 'revenue'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                  activeTab === tab
                    ? 'bg-blue-600 text-white'
                    : 'text-blue-200 hover:bg-white/10'
                }`}
              >
                {tab.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
              </button>
            ))}
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && overview && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard title="Total Clients" value={overview.total_clients} color="bg-gradient-to-br from-blue-600 to-blue-700" />
                <StatCard title="Total Bookings" value={overview.total_bookings} color="bg-gradient-to-br from-green-600 to-green-700" />
                <StatCard 
                  title="Completion Rate" 
                  value={`${overview.completion_rate}%`} 
                  subtitle={`${overview.confirmed_bookings} confirmed`}
                  color="bg-gradient-to-br from-blue-600 to-blue-700"
                />
                <StatCard 
                  title="Upcoming Sessions" 
                  value={overview.upcoming_bookings} 
                  subtitle={`${overview.pending_bookings} pending`}
                  color="bg-gradient-to-br from-orange-600 to-orange-700"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <StatCard title="Confirmed" value={overview.confirmed_bookings} color="bg-gradient-to-br from-emerald-600 to-emerald-700" />
                <StatCard title="Pending" value={overview.pending_bookings} color="bg-gradient-to-br from-yellow-600 to-yellow-700" />
                <StatCard title="Cancelled" value={overview.cancelled_bookings} color="bg-gradient-to-br from-red-600 to-red-700" />
              </div>
            </div>
          )}

          {/* Booking Trends Tab */}
          {activeTab === 'trends' && (
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Booking Trends (Last 30 Days)</h2>
              <div className="space-y-2">
                {bookingTrends.map((trend) => (
                  <div key={trend.date} className="bg-white/5 rounded-lg p-3">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                      <span className="text-blue-200">{new Date(trend.date).toLocaleDateString()}</span>
                      <div className="flex flex-wrap gap-2 sm:gap-4">
                        <span className="text-green-400 text-sm">Confirmed: {trend.confirmed}</span>
                        <span className="text-yellow-400 text-sm">Pending: {trend.pending}</span>
                        <span className="text-red-400 text-sm">Cancelled: {trend.cancelled}</span>
                        <span className="text-white font-bold text-sm">Total: {trend.total}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Client Stats Tab */}
          {activeTab === 'clients' && (
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Client Statistics</h2>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[600px]">
                  <thead>
                    <tr className="border-b border-white/20">
                      <th className="text-left p-3 text-blue-200 text-sm whitespace-nowrap">Client Name</th>
                      <th className="text-left p-3 text-blue-200 text-sm whitespace-nowrap hidden sm:table-cell">Email</th>
                      <th className="text-center p-3 text-blue-200 text-sm whitespace-nowrap">Total Sessions</th>
                      <th className="text-center p-3 text-blue-200 text-sm whitespace-nowrap">Completed</th>
                      <th className="text-center p-3 text-blue-200 text-sm whitespace-nowrap hidden md:table-cell">Cancelled</th>
                      <th className="text-center p-3 text-blue-200 text-sm whitespace-nowrap">Completion Rate</th>
                      <th className="text-center p-3 text-blue-200 text-sm whitespace-nowrap hidden lg:table-cell">Last Session</th>
                    </tr>
                  </thead>
                  <tbody>
                    {clientStats.map((client) => (
                      <tr key={client.client_id} className="border-b border-white/10 hover:bg-white/5">
                        <td className="p-3 text-white text-sm">{client.client_name}</td>
                        <td className="p-3 text-blue-200 text-sm hidden sm:table-cell">{client.client_email}</td>
                        <td className="p-3 text-center text-white font-bold text-sm">{client.total_sessions}</td>
                        <td className="p-3 text-center text-green-400 text-sm">{client.completed_sessions}</td>
                        <td className="p-3 text-center text-red-400 text-sm hidden md:table-cell">{client.cancelled_sessions}</td>
                        <td className="p-3 text-center text-white text-sm">{client.completion_rate}%</td>
                        <td className="p-3 text-center text-blue-200 text-sm hidden lg:table-cell">
                          {client.last_session_date ? new Date(client.last_session_date).toLocaleDateString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Time Slots Tab */}
          {activeTab === 'time-slots' && (
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Popular Time Slots</h2>
              <div className="space-y-3">
                {timeSlots.map((slot) => (
                  <div key={slot.hour} className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                    <span className="text-blue-200 w-full sm:w-24 text-sm">{slot.time_label}</span>
                    <div className="flex-1 bg-white/10 rounded-full h-6 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 h-full transition-all duration-500"
                        style={{ width: `${(slot.count / Math.max(...timeSlots.map(s => s.count))) * 100}%` }}
                      />
                    </div>
                    <span className="text-white font-bold w-full sm:w-16 text-right text-sm">{slot.count} sessions</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Revenue Tab */}
          {activeTab === 'revenue' && (
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Monthly Revenue (Last 6 Months)</h2>
              <div className="space-y-3">
                {revenueData.map((month) => (
                  <div key={month.month} className="flex flex-col sm:flex-row sm:items-center sm:justify-between bg-white/5 rounded-lg p-4 gap-2">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
                      <span className="text-white font-bold text-sm">{new Date(month.month + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
                      <span className="text-blue-200 text-sm">{month.sessions} sessions</span>
                    </div>
                    <span className="text-green-400 text-xl sm:text-2xl font-bold">Rs {month.revenue}</span>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-white/20">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                  <span className="text-blue-200 text-sm">Total Revenue (6 months)</span>
                  <span className="text-white text-2xl sm:text-3xl font-bold">Rs {revenueData.reduce((sum, m) => sum + m.revenue, 0)}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  )
}
