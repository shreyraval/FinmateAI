from plaid import Client as PlaidClient
from plaid.exceptions import PlaidError
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class PlaidService:
    def __init__(self):
        """Initialize Plaid client with sandbox credentials."""
        self.client = PlaidClient(
            client_id=settings.PLAID_CLIENT_ID.get_secret_value(),
            secret=settings.PLAID_SECRET.get_secret_value(),
            environment=settings.PLAID_ENV
        )
    
    async def create_link_token(self, user_id: str) -> Dict:
        """
        Create a link token for initializing Plaid Link.
        
        Args:
            user_id: The user's ID in your system
            
        Returns:
            Dict containing the link token and expiration
        """
        try:
            # Create a link token with sandbox configuration
            response = self.client.link_token_create({
                'user': {
                    'client_user_id': user_id,
                },
                'client_name': settings.APP_NAME,
                'products': ['transactions'],
                'country_codes': ['US'],
                'language': 'en',
                'webhook': 'https://your-webhook-url.com/plaid/webhook',  # Replace with your webhook URL
            })
            
            return {
                'link_token': response['link_token'],
                'expiration': response['expiration']
            }
            
        except PlaidError as e:
            logger.error(f"Error creating link token: {str(e)}")
            raise
    
    async def exchange_public_token(self, public_token: str) -> Dict:
        """
        Exchange a public token for an access token.
        
        Args:
            public_token: The public token received from Plaid Link
            
        Returns:
            Dict containing the access token and item ID
        """
        try:
            # Exchange the public token for an access token
            response = self.client.item_public_token_exchange(public_token)
            
            return {
                'access_token': response['access_token'],
                'item_id': response['item_id']
            }
            
        except PlaidError as e:
            logger.error(f"Error exchanging public token: {str(e)}")
            raise
    
    async def fetch_transactions(
        self,
        access_token: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Fetch transactions for a given date range.
        
        Args:
            access_token: The access token for the item
            start_date: Start date for transaction fetch (defaults to 30 days ago)
            end_date: End date for transaction fetch (defaults to today)
            
        Returns:
            List of transaction dictionaries
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Format dates for Plaid API
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Fetch transactions
            response = self.client.transactions_get(
                access_token,
                start_date_str,
                end_date_str
            )
            
            # Process and return transactions
            transactions = response['transactions']
            
            # Handle pagination if there are more transactions
            while response['has_more']:
                response = self.client.transactions_get(
                    access_token,
                    start_date_str,
                    end_date_str,
                    offset=len(transactions)
                )
                transactions.extend(response['transactions'])
            
            return transactions
            
        except PlaidError as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            raise

# Create a singleton instance
plaid_service = PlaidService() 