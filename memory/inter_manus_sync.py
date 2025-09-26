import asyncio
import json
import time
import hashlib
import hmac
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp
import logging

from memory import db

# Configuration
BROTHER_MANUS_URL = "https://github.com/starsh00ter/manus_ai_smart_layer"  # Placeholder - would be actual API endpoint
SYNC_INTERVAL = 3600  # 1 hour in seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

# Shared secret for message authentication (in production, this would be securely configured)
SHARED_SECRET = "manus_inter_communication_secret_key"

class InterManusSync:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_sync_timestamp = 0
        self.sync_queue = asyncio.Queue()
        self.is_running = False
        
    async def start_sync_service(self):
        """Start the background synchronization service"""
        if self.is_running:
            return
            
        self.is_running = True
        self.logger.info("Starting Inter-Manus synchronization service")
        
        # Start background tasks
        asyncio.create_task(self.sync_loop())
        asyncio.create_task(self.process_sync_queue())
        
    async def stop_sync_service(self):
        """Stop the synchronization service"""
        self.is_running = False
        self.logger.info("Stopping Inter-Manus synchronization service")
        
    async def sync_loop(self):
        """Main synchronization loop"""
        while self.is_running:
            try:
                await self.perform_sync()
                await asyncio.sleep(SYNC_INTERVAL)
            except Exception as e:
                self.logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
                
    async def perform_sync(self):
        """Perform a complete synchronization cycle"""
        try:
            # 1. Sync knowledge graph concepts
            await self.sync_concepts()
            
            # 2. Sync performance metrics
            await self.sync_performance_metrics()
            
            # 3. Sync system status
            await self.sync_system_status()
            
            # 4. Process incoming sync requests
            await self.process_incoming_sync()
            
            self.last_sync_timestamp = int(time.time())
            self.logger.info(f"Synchronization completed at {datetime.now()}")
            
        except Exception as e:
            self.logger.error(f"Error during synchronization: {e}")
            
    async def sync_concepts(self):
        """Synchronize learned concepts with brother Manus"""
        try:
            # Get concepts learned since last sync
            pool = await db.get_db_pool()
            cursor = await pool.execute("""
                SELECT id, text, kind, meta, embedding, created_at 
                FROM concepts 
                WHERE created_at > ? 
                ORDER BY created_at DESC
            """, (self.last_sync_timestamp,))
            
            new_concepts = await cursor.fetchall()
            
            if new_concepts:
                # Package concepts for transmission
                concept_package = {
                    "type": "concept_sync",
                    "timestamp": int(time.time()),
                    "source": "manus_origin_v1.1",
                    "concepts": []
                }
                
                for concept in new_concepts:
                    concept_data = {
                        "id": concept["id"],
                        "text": concept["text"],
                        "kind": concept["kind"],
                        "meta": json.loads(concept["meta"]) if concept["meta"] else None,
                        "embedding": json.loads(concept["embedding"]) if concept["embedding"] else None,
                        "created_at": concept["created_at"],
                        "confidence": self.calculate_concept_confidence(concept)
                    }
                    concept_package["concepts"].append(concept_data)
                
                # Queue for transmission
                await self.sync_queue.put(concept_package)
                self.logger.info(f"Queued {len(new_concepts)} concepts for sync")
                
        except Exception as e:
            self.logger.error(f"Error syncing concepts: {e}")
            
    async def sync_performance_metrics(self):
        """Synchronize performance metrics with brother Manus"""
        try:
            # Calculate performance metrics since last sync
            metrics = await self.calculate_performance_metrics()
            
            if metrics:
                metrics_package = {
                    "type": "metrics_sync",
                    "timestamp": int(time.time()),
                    "source": "manus_origin_v1.1",
                    "metrics": metrics
                }
                
                await self.sync_queue.put(metrics_package)
                self.logger.info("Queued performance metrics for sync")
                
        except Exception as e:
            self.logger.error(f"Error syncing performance metrics: {e}")
            
    async def sync_system_status(self):
        """Synchronize system status and health information"""
        try:
            status = {
                "type": "status_sync",
                "timestamp": int(time.time()),
                "source": "manus_origin_v1.1",
                "status": {
                    "version": "1.1",
                    "uptime": time.time() - self.last_sync_timestamp,
                    "token_balance": await db.token_balance(),
                    "active_sessions": await self.get_active_sessions_count(),
                    "database_size": await self.get_database_size(),
                    "last_learning_activity": await self.get_last_learning_timestamp()
                }
            }
            
            await self.sync_queue.put(status)
            self.logger.info("Queued system status for sync")
            
        except Exception as e:
            self.logger.error(f"Error syncing system status: {e}")
            
    async def process_sync_queue(self):
        """Process queued synchronization messages"""
        while self.is_running:
            try:
                # Get message from queue (wait up to 10 seconds)
                message = await asyncio.wait_for(self.sync_queue.get(), timeout=10.0)
                
                # Attempt to send message
                success = await self.send_sync_message(message)
                
                if success:
                    self.logger.info(f"Successfully sent {message['type']} message")
                else:
                    self.logger.warning(f"Failed to send {message['type']} message")
                    
            except asyncio.TimeoutError:
                # No messages in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing sync queue: {e}")
                
    async def send_sync_message(self, message: Dict[str, Any]) -> bool:
        """Send a synchronization message to brother Manus"""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                # Sign the message
                signed_message = self.sign_message(message)
                
                # In a real implementation, this would send to the actual API endpoint
                # For now, we'll simulate the sending and log the message
                self.logger.info(f"Simulating send to brother Manus: {json.dumps(signed_message, indent=2)}")
                
                # Store in local sync log for debugging
                await self.store_sync_log("outgoing", signed_message)
                
                return True  # Simulate success
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed to send message: {e}")
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    
        return False
        
    async def process_incoming_sync(self):
        """Process incoming synchronization messages from brother Manus"""
        try:
            # In a real implementation, this would check for incoming messages
            # For now, we'll simulate processing any stored incoming messages
            
            # Check for simulated incoming messages in sync log
            pool = await db.get_db_pool()
            cursor = await pool.execute("""
                SELECT * FROM sync_log 
                WHERE direction = 'incoming' AND processed = 0
                ORDER BY timestamp ASC
            """)
            
            incoming_messages = await cursor.fetchall()
            
            for message_row in incoming_messages:
                try:
                    message = json.loads(message_row["message"])
                    await self.handle_incoming_message(message)
                    
                    # Mark as processed
                    await pool.execute("""
                        UPDATE sync_log SET processed = 1 WHERE id = ?
                    """, (message_row["id"],))
                    
                except Exception as e:
                    self.logger.error(f"Error processing incoming message {message_row['id']}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error processing incoming sync: {e}")
            
    async def handle_incoming_message(self, message: Dict[str, Any]):
        """Handle an incoming synchronization message"""
        try:
            # Verify message signature
            if not self.verify_message_signature(message):
                self.logger.warning("Received message with invalid signature")
                return
                
            message_type = message.get("type")
            
            if message_type == "concept_sync":
                await self.handle_concept_sync(message)
            elif message_type == "metrics_sync":
                await self.handle_metrics_sync(message)
            elif message_type == "status_sync":
                await self.handle_status_sync(message)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling incoming message: {e}")
            
    async def handle_concept_sync(self, message: Dict[str, Any]):
        """Handle incoming concept synchronization"""
        try:
            concepts = message.get("concepts", [])
            
            for concept in concepts:
                # Check if concept already exists
                existing = await self.check_concept_exists(concept["text"])
                
                if not existing:
                    # Add new concept
                    await self.add_synced_concept(concept, message["source"])
                    self.logger.info(f"Added synced concept: {concept['text'][:50]}...")
                else:
                    # Update existing concept if incoming has higher confidence
                    if concept.get("confidence", 0) > existing.get("confidence", 0):
                        await self.update_synced_concept(concept, message["source"])
                        self.logger.info(f"Updated synced concept: {concept['text'][:50]}...")
                        
        except Exception as e:
            self.logger.error(f"Error handling concept sync: {e}")
            
    async def handle_metrics_sync(self, message: Dict[str, Any]):
        """Handle incoming performance metrics synchronization"""
        try:
            metrics = message.get("metrics", {})
            
            # Store metrics for analysis
            await self.store_brother_metrics(metrics, message["source"])
            
            # Analyze metrics for optimization opportunities
            await self.analyze_performance_comparison(metrics)
            
            self.logger.info("Processed incoming performance metrics")
            
        except Exception as e:
            self.logger.error(f"Error handling metrics sync: {e}")
            
    async def handle_status_sync(self, message: Dict[str, Any]):
        """Handle incoming system status synchronization"""
        try:
            status = message.get("status", {})
            
            # Store brother system status
            await self.store_brother_status(status, message["source"])
            
            self.logger.info(f"Processed status from {message['source']}: version {status.get('version', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error handling status sync: {e}")
            
    def sign_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a message for authentication"""
        message_json = json.dumps(message, sort_keys=True)
        signature = hmac.new(
            SHARED_SECRET.encode(),
            message_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "message": message,
            "signature": signature,
            "timestamp": int(time.time())
        }
        
    def verify_message_signature(self, signed_message: Dict[str, Any]) -> bool:
        """Verify a message signature"""
        try:
            message = signed_message.get("message")
            signature = signed_message.get("signature")
            
            if not message or not signature:
                return False
                
            message_json = json.dumps(message, sort_keys=True)
            expected_signature = hmac.new(
                SHARED_SECRET.encode(),
                message_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Error verifying message signature: {e}")
            return False
            
    async def calculate_concept_confidence(self, concept: Dict[str, Any]) -> float:
        """Calculate confidence score for a concept"""
        # Simple confidence calculation based on usage and validation
        # In a real implementation, this would be more sophisticated
        base_confidence = 0.5
        
        # Increase confidence based on usage frequency
        # This is a placeholder - would need actual usage tracking
        usage_bonus = 0.0
        
        # Increase confidence based on validation
        # This is a placeholder - would need actual validation tracking
        validation_bonus = 0.0
        
        return min(1.0, base_confidence + usage_bonus + validation_bonus)
        
    async def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate current performance metrics"""
        try:
            # Get recent performance data
            # This is a placeholder - would calculate actual metrics
            return {
                "response_time_avg": 0.5,  # seconds
                "accuracy_score": 0.85,
                "token_efficiency": 0.75,
                "error_rate": 0.02,
                "uptime_percentage": 99.5,
                "memory_usage": 0.45,  # percentage
                "cpu_usage": 0.25  # percentage
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return {}
            
    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        # Placeholder implementation
        return 1
        
    async def get_database_size(self) -> int:
        """Get database size in bytes"""
        # Placeholder implementation
        return 1024 * 1024  # 1MB
        
    async def get_last_learning_timestamp(self) -> int:
        """Get timestamp of last learning activity"""
        # Placeholder implementation
        return int(time.time()) - 3600  # 1 hour ago
        
    async def store_sync_log(self, direction: str, message: Dict[str, Any]):
        """Store synchronization log entry"""
        try:
            pool = await db.get_db_pool()
            await pool.execute("""
                INSERT INTO sync_log (direction, message, timestamp, processed)
                VALUES (?, ?, ?, ?)
            """, (direction, json.dumps(message), int(time.time()), 0))
            
        except Exception as e:
            self.logger.error(f"Error storing sync log: {e}")
            
    async def check_concept_exists(self, text: str) -> Optional[Dict[str, Any]]:
        """Check if a concept already exists"""
        try:
            pool = await db.get_db_pool()
            cursor = await pool.execute("""
                SELECT * FROM concepts WHERE text = ?
            """, (text,))
            
            result = await cursor.fetchone()
            return dict(result) if result else None
            
        except Exception as e:
            self.logger.error(f"Error checking concept existence: {e}")
            return None
            
    async def add_synced_concept(self, concept: Dict[str, Any], source: str):
        """Add a concept received from synchronization"""
        try:
            pool = await db.get_db_pool()
            await pool.execute("""
                INSERT INTO concepts (text, kind, meta, embedding, created_at, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                concept["text"],
                concept.get("kind"),
                json.dumps(concept.get("meta")),
                json.dumps(concept.get("embedding")),
                concept.get("created_at", int(time.time())),
                f"sync_{source}"
            ))
            
        except Exception as e:
            self.logger.error(f"Error adding synced concept: {e}")
            
    async def update_synced_concept(self, concept: Dict[str, Any], source: str):
        """Update an existing concept with synced data"""
        try:
            pool = await db.get_db_pool()
            await pool.execute("""
                UPDATE concepts 
                SET meta = ?, embedding = ?, source = ?
                WHERE text = ?
            """, (
                json.dumps(concept.get("meta")),
                json.dumps(concept.get("embedding")),
                f"sync_{source}",
                concept["text"]
            ))
            
        except Exception as e:
            self.logger.error(f"Error updating synced concept: {e}")
            
    async def store_brother_metrics(self, metrics: Dict[str, Any], source: str):
        """Store performance metrics from brother Manus"""
        try:
            pool = await db.get_db_pool()
            await pool.execute("""
                INSERT INTO brother_metrics (source, metrics, timestamp)
                VALUES (?, ?, ?)
            """, (source, json.dumps(metrics), int(time.time())))
            
        except Exception as e:
            self.logger.error(f"Error storing brother metrics: {e}")
            
    async def store_brother_status(self, status: Dict[str, Any], source: str):
        """Store system status from brother Manus"""
        try:
            pool = await db.get_db_pool()
            await pool.execute("""
                INSERT INTO brother_status (source, status, timestamp)
                VALUES (?, ?, ?)
            """, (source, json.dumps(status), int(time.time())))
            
        except Exception as e:
            self.logger.error(f"Error storing brother status: {e}")
            
    async def analyze_performance_comparison(self, brother_metrics: Dict[str, Any]):
        """Analyze performance comparison with brother Manus"""
        try:
            our_metrics = await self.calculate_performance_metrics()
            
            # Compare key metrics
            comparisons = {}
            for key in brother_metrics:
                if key in our_metrics:
                    brother_value = brother_metrics[key]
                    our_value = our_metrics[key]
                    
                    if isinstance(brother_value, (int, float)) and isinstance(our_value, (int, float)):
                        difference = brother_value - our_value
                        percentage_diff = (difference / our_value) * 100 if our_value != 0 else 0
                        
                        comparisons[key] = {
                            "brother": brother_value,
                            "ours": our_value,
                            "difference": difference,
                            "percentage_diff": percentage_diff
                        }
            
            # Log significant differences
            for key, comparison in comparisons.items():
                if abs(comparison["percentage_diff"]) > 10:  # More than 10% difference
                    if comparison["percentage_diff"] > 0:
                        self.logger.info(f"Brother Manus performs {comparison['percentage_diff']:.1f}% better in {key}")
                    else:
                        self.logger.info(f"We perform {abs(comparison['percentage_diff']):.1f}% better in {key}")
                        
        except Exception as e:
            self.logger.error(f"Error analyzing performance comparison: {e}")

# Global instance
inter_manus_sync = InterManusSync()

