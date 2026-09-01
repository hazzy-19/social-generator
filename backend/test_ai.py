import asyncio
from app.ai.client import complete

async def main():
    print("Sending prompt to AI...")
    try:
        response = await complete("Write a short limerick about the wonders of GPU computing.")
        print("\nAI Response:")
        print("-" * 20)
        print(response)
        print("-" * 20)
        print("\nAI is working successfully!")
    except Exception as e:
        print(f"\nAI connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
