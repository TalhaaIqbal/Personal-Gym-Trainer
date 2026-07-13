from ..repositories.booking_repository import BookingRepository
from ..repositories.user_repository import UserRepository
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

PER_SESSION_COST = 2500

class AnalyticsService:
    def __init__(self):
        self.bookings_collection = db["bookings"]
        self.users_collection = db["users"]
        self.booking_repository = BookingRepository(self.bookings_collection)
        self.user_repository = UserRepository(self.users_collection)

    async def get_trainer_overview(self, trainer_id: str) -> Dict[str, Any]:
        try:
            # Get all bookings for trainer
            all_bookings = await self.booking_repository.get_by_trainer_id(trainer_id)
            
            # Get all clients
            client_ids = list(set([b["client_id"] for b in all_bookings]))
            total_clients = len(client_ids)
            
            #Booking stats
            total_bookings = len(all_bookings)
            confirmed_bookings = len([b for b in all_bookings if b.get("status") == "confirmed"])
            pending_bookings = len([b for b in all_bookings if b.get("status") == "pending"])
            cancelled_bookings = len([b for b in all_bookings if b.get("status") == "cancelled"])
            
            completion_rate = (confirmed_bookings / total_bookings * 100) if total_bookings > 0 else 0
            
            # Get bookings from last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_bookings = [b for b in all_bookings 
                             if datetime.strptime(b["booking_date"], "%Y-%m-%d") >= thirty_days_ago]
            
            return {
                "total_clients": total_clients,
                "total_bookings": total_bookings,
                "confirmed_bookings": confirmed_bookings,
                "pending_bookings": pending_bookings,
                "cancelled_bookings": cancelled_bookings,
                "completion_rate": round(completion_rate, 2),
                "recent_bookings": len(recent_bookings),
                "upcoming_bookings": len([b for b in all_bookings 
                                        if b.get("status") in ["confirmed", "pending"] 
                                        and datetime.strptime(b["booking_date"], "%Y-%m-%d") >= datetime.now()])
            }
        except Exception as e:
            print(f"Error getting trainer overview: {e}")
            raise

    async def get_booking_trends(self, trainer_id: str, days: int = 30) -> List[Dict[str, Any]]:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            all_bookings = await self.booking_repository.get_by_trainer_id(trainer_id)
            
            # Filter bookings by date range
            filtered_bookings = [b for b in all_bookings 
                               if start_date <= datetime.strptime(b["booking_date"], "%Y-%m-%d") <= end_date]
            
            # Group by date
            daily_bookings = defaultdict(lambda: {"confirmed": 0, "pending": 0, "cancelled": 0})
            
            for booking in filtered_bookings:
                booking_date = booking["booking_date"]
                status = booking.get("status", "pending")
                daily_bookings[booking_date][status] += 1
            
            trends = []
            for date in sorted(daily_bookings.keys()):
                trends.append({
                    "date": date,
                    "confirmed": daily_bookings[date]["confirmed"],
                    "pending": daily_bookings[date]["pending"],
                    "cancelled": daily_bookings[date]["cancelled"],
                    "total": sum(daily_bookings[date].values())
                })
            
            return trends
        except Exception as e:
            print(f"Error getting booking trends: {e}")
            raise

    async def get_client_stats(self, trainer_id: str) -> List[Dict[str, Any]]:
        try:
            all_bookings = await self.booking_repository.get_by_trainer_id(trainer_id)
            
            client_bookings = defaultdict(list)
            for booking in all_bookings:
                client_bookings[booking["client_id"]].append(booking)
            
            client_stats = []
            for client_id, bookings in client_bookings.items():
                client = await self.user_repository.get_by_id(client_id)
                if not client:
                    continue
                
                total_sessions = len(bookings)
                completed_sessions = len([b for b in bookings if b.get("status") == "confirmed"])
                cancelled_sessions = len([b for b in bookings if b.get("status") == "cancelled"])
                
                # Get last booking date (max = latest)
                last_booking = max(bookings, key=lambda b: b["booking_date"]) if bookings else None
                last_session_date = last_booking["booking_date"] if last_booking else None
                
                client_stats.append({
                    "client_id": client_id,
                    "client_name": client.get("name", "Unknown"),
                    "client_email": client.get("email", ""),
                    "total_sessions": total_sessions,
                    "completed_sessions": completed_sessions,
                    "cancelled_sessions": cancelled_sessions,
                    "completion_rate": round((completed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 2),
                    "last_session_date": last_session_date
                })
            
            client_stats.sort(key=lambda x: x["total_sessions"], reverse=True)
            
            return client_stats
        except Exception as e:
            print(f"Error getting client stats: {e}")
            raise

    async def get_time_slot_analysis(self, trainer_id: str) -> List[Dict[str, Any]]:
        try:
            all_bookings = await self.booking_repository.get_by_trainer_id(trainer_id)
            
            # Group by hour
            hour_bookings = defaultdict(int)
            for booking in all_bookings:
                if booking.get("status") in ["confirmed", "pending"]:
                    hour = int(booking["start_time"].split(":")[0])
                    hour_bookings[hour] += 1
            
            time_slots = []
            for hour in sorted(hour_bookings.keys()):
                time_slots.append({
                    "hour": hour,
                    "count": hour_bookings[hour],
                    "time_label": f"{hour % 12 or 12}:00 {'PM' if hour >= 12 else 'AM'}"
                })
            
            return time_slots
        except Exception as e:
            print(f"Error getting time slot analysis: {e}")
            raise

    async def get_monthly_revenue(self, trainer_id: str, months: int = 6) -> List[Dict[str, Any]]:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30 * months)
            
            all_bookings = await self.booking_repository.get_by_trainer_id(trainer_id)
            
            # Filter confirmed bookings by date range
            filtered_bookings = [b for b in all_bookings 
                               if b.get("status") == "confirmed"
                               and start_date <= datetime.strptime(b["booking_date"], "%Y-%m-%d") <= end_date]
            
            # Group by month
            monthly_revenue = defaultdict(int)
            for booking in filtered_bookings:
                booking_date = datetime.strptime(booking["booking_date"], "%Y-%m-%d")
                month_key = booking_date.strftime("%Y-%m")
                monthly_revenue[month_key] += PER_SESSION_COST
            
            # Convert to sorted list
            revenue_trends = []
            for month in sorted(monthly_revenue.keys()):
                revenue_trends.append({
                    "month": month,
                    "revenue": monthly_revenue[month],
                    "sessions": monthly_revenue[month] // PER_SESSION_COST
                })
            
            return revenue_trends
        except Exception as e:
            print(f"Error getting monthly revenue: {e}")
            raise
