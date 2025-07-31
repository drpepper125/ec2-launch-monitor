import boto3
import requests
import json
from typing import Optional, Dict, Any


class EC2APIHandler:
    """
    Handles EC2 instance data retrieval and API communication workflow
    """
    
    def __init__(self, instance_id: str, api_base_url: str = "http://localhost:5001/api"):
        self.instance_id = instance_id
        self.api_base_url = api_base_url
        
        # AWS clients
        self.ec2_client = boto3.client('ec2')
        self.secrets_client = boto3.client('secretsmanager')
        
        # State management
        self.instance_data: Optional[Dict] = None
        self.token: Optional[str] = None
        self.registration_id: Optional[str] = None
        self.registration_response: Optional[Dict] = None
        
    def fetch_instance_details(self) -> Dict[str, Any]:
        """
        Fetch EC2 instance details from AWS
        """
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            
            if not response['Reservations']:
                raise ValueError(f"Instance {self.instance_id} not found")
            
            instance = response['Reservations'][0]['Instances'][0]
            
            self.instance_data = {
                'instance_id': self.instance_id,
                'ip_address': instance.get('PublicIpAddress', 'N/A'),
                'private_dns': instance.get('PrivateDnsName', 'N/A'),
                'private_ip': instance.get('PrivateIpAddress', 'N/A'),
                'state': instance['State']['Name'],
                'instance_type': instance['InstanceType']
            }
            
            print(f"✅ Fetched details for instance: {self.instance_id}")
            return self.instance_data
            
        except Exception as e:
            print(f"❌ Error fetching instance details: {str(e)}")
            # For demo purposes, create mock data
            self.instance_data = {
                'instance_id': self.instance_id,
                'ip_address': '192.168.1.100',
                'private_dns': f'ip-192-168-1-100.{self.instance_id}.ec2.internal',
                'private_ip': '192.168.1.100',
                'state': 'running',
                'instance_type': 't3.micro'
            }
            print("📝 Using mock data for demo")
            return self.instance_data
    
    def get_secrets(self, client_id_secret_name: str = None, client_secret_secret_name: str = None) -> tuple[str, str]:
        """
        Get secrets from AWS Secrets Manager
        
        Args:
            client_id_secret_name: Name of the secret containing client_id
            client_secret_secret_name: Name of the secret containing client_secret
            
        Returns:
            Tuple containing (client_id, client_secret) in that order
        """
        try:
            if client_id_secret_name and client_secret_secret_name:
                # Get individual secrets
                client_id_response = self.secrets_client.get_secret_value(SecretName=client_id_secret_name)
                client_secret_response = self.secrets_client.get_secret_value(SecretName=client_secret_secret_name)
                
                # Return the actual secret string values as tuple
                return (
                    client_id_response['SecretString'],
                    client_secret_response['SecretString']
                )
                
            elif client_id_secret_name:
                # Get both from a single secret (assumes JSON format)
                response = self.secrets_client.get_secret_value(SecretName=client_id_secret_name)
                secrets = json.loads(response['SecretString'])
                
                # Return the values from the JSON as tuple
                return (
                    secrets['client_id'],
                    secrets['client_secret']
                )
            else:
                raise ValueError("Must provide secret name(s)")
            
            print(f"✅ Retrieved secrets successfully")
            
        except Exception as e:
            print(f"❌ Error getting secrets: {str(e)}")
            # Return mock secrets for demo as tuple
            return (
                'demo_client_id_123',
                'demo_client_secret_456'
            )
    
    def get_token(self, client_id_secret_name: str = None, client_secret_secret_name: str = None) -> bool:
        """
        Step 1: Register with the API and get token
        
        Args:
            client_id_secret_name: Name of secret containing client_id (or combined secret)
            client_secret_secret_name: Name of secret containing client_secret (optional if using combined)
        """
        try:
            # Get credentials
            if client_id_secret_name or client_secret_secret_name:
                client_id, client_secret = self.get_secrets(client_id_secret_name, client_secret_secret_name)
            else:
                # Use demo credentials when no secrets specified
                client_id = 'demo_client_id_123'
                client_secret = 'demo_client_secret_456'
            
            payload = {
                'client_id': client_id,
                'client_secret': client_secret,
                'other_details': f'Registration for instance {self.instance_id}'
            }
            
            response = requests.post(
                f"{self.api_base_url}/register",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.token = result['token']
                print(f"✅ Token acquired: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Token acquisition failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting token: {str(e)}")
            return False
    
    def send_payload(self) -> bool:
        """
        Step 2: Send EC2 instance data to the API
        """
        if not self.token:
            print("❌ No token available. Call get_token() first.")
            return False
        
        if not self.instance_data:
            print("❌ No instance data available. Call fetch_instance_details() first.")
            return False
        
        try:
            payload = {
                'token': self.token,
                'instance_id': self.instance_data['instance_id'],
                'ip_address': self.instance_data['ip_address'],
                'private_dns': self.instance_data['private_dns']
            }
            
            response = requests.post(
                f"{self.api_base_url}/submit-instance",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.registration_id = result['registration_id']
                self.registration_response = result
                print(f"✅ Instance data submitted. Registration ID: {self.registration_id}")
                return True
            else:
                print(f"❌ Failed to submit instance data: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending payload: {str(e)}")
            return False
    
    def get_status(self) -> Optional[Dict]:
        """
        Step 3: Check the status of the registration
        """
        if not self.token:
            print("❌ No token available.")
            return None
        
        if not self.registration_id:
            print("❌ No registration ID available. Call send_payload() first.")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_base_url}/status/{self.registration_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result['status']}")
                return result
            else:
                print(f"❌ Failed to get status: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting status: {str(e)}")
            return None
    
    def process_instance_registration(self, client_id_secret_name: str = None, client_secret_secret_name: str = None) -> Optional[Dict]:
        """
        Complete workflow: fetch details, get token, send payload, check status
        
        Args:
            client_id_secret_name: Name of secret containing client_id (or combined secret)
            client_secret_secret_name: Name of secret containing client_secret (optional if using combined)
        """
        print(f"🚀 Starting registration process for instance: {self.instance_id}")
        
        # Step 1: Fetch instance details
        self.fetch_instance_details()
        
        # Step 2: Get token
        if not self.get_token(client_id_secret_name, client_secret_secret_name):
            return None
        
        # Step 3: Send payload
        if not self.send_payload():
            return None
        
        # Step 4: Check status
        return self.get_status()


# Legacy function for backward compatibility
def get_ec2_details(client=None):
    """Legacy function - consider using EC2APIHandler class instead"""
    ec2_client = client or boto3.client('ec2')
    response = ec2_client.describe_instances()
    ec2_list = [reservation for reservation in response.get('Reservations', [])]
    return ec2_list

    

