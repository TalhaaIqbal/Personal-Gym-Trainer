from .base import BaseRepository
from ..models.booking import Booking

class BookingRepository(BaseRepository[Booking]):
    async def get_by_client_id(self, client_id: str, status: str = None):
        query = {"client_id": client_id}
        if status:
            query["status"] = status
        return await self.collection.find(query).to_list(length=None)
    
    async def get_by_trainer_id(self, trainer_id: str, status: str = None):
        query = {"trainer_id": trainer_id}
        if status:
            query["status"] = status
        return await self.collection.find(query).to_list(length=None)
    
    async def get_by_client_and_trainer(self, client_id: str, trainer_id: str):
        return await self.collection.find({"client_id": client_id, "trainer_id": trainer_id}).to_list(length=None)

    async def get_by_client_id_with_trainer_info(self, client_id: str):
        pipeline = [
            {
                "$match": {"client_id": client_id}
            },
            {
                "$lookup": {  #Left join
                    "from": "users",
                    "let" : {
                        "tid": "$trainer_id"
                    },
                    "pipeline": [  #Sub pipeline (or query)
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": ["$_id", { #On users._id = booking.trainer_id
                                        "$toObjectId": "$$tid" #Convert string to ObjectId
                                    }]
                                }

                            }
                        },
                        {
                            "$project": { #get these 2 fields
                                "name": 1,
                                "email": 1
                            }
                        }
                    ],
                    "as": "trainer_info"
                }
            },
            {
                "$unwind": {  #Flatten the trainer_info array into single object
                    "path": "$trainer_info",
                    "preserveNullAndEmptyArrays": True #No deletion of empty records
                }
            },
        ]
        
        cursor = await self.collection.aggregate(pipeline) 
        return await cursor.to_list(length=None) 