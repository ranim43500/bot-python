import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_webhook():
    token = "7426449390:AAFvKcfiKArCsnd9_KpY6sETzK1VL4IJHtA"
    base_url = f"https://api.telegram.org/bot{token}"
    
    # Delete webhook
    logger.info("Deleting webhook...")
    response = requests.get(f"{base_url}/deleteWebhook?drop_pending_updates=true")
    logger.info(f"Delete webhook response: {response.status_code} - {response.text}")
    
    # Ensure the webhook is really gone
    time.sleep(3)
    
    # Check getWebhookInfo
    response = requests.get(f"{base_url}/getWebhookInfo")
    logger.info(f"Get webhook info response: {response.status_code} - {response.text}")
    
    return response.status_code == 200

if __name__ == "__main__":
    if reset_webhook():
        logger.info("Webhook successfully reset. You can now run the bot.")
    else:
        logger.error("Failed to reset webhook.") 