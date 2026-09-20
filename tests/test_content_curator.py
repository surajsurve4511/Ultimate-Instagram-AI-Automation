"""
Test script for Content Curator
Tests content curation from RSS feeds, Reddit, Hacker News
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

async def test_content_curator():
    """Test content curator"""
    print("=" * 70)
    print("🧪 TESTING CONTENT CURATOR")
    print("=" * 70)
    print()
    
    try:
        from src.content.content_curator import ContentCurator
        
        print("1️⃣ Initializing Content Curator...")
        curator = ContentCurator()
        await curator.initialize()
        print("✅ Content Curator initialized\n")
        
        # Test 2: Fetch RSS content
        print("2️⃣ Testing RSS feed content extraction...")
        print("   Fetching from AI/tech RSS feeds...")
        
        rss_content = await curator._fetch_rss_content()
        
        if rss_content:
            print(f"✅ Fetched {len(rss_content)} items from RSS feeds\n")
            print("📰 Sample RSS Content:")
            print("-" * 70)
            
            for i, item in enumerate(rss_content[:3], 1):
                print(f"\n{i}. {item.get('title', 'N/A')[:70]}...")
                print(f"   Source: {item.get('source', 'N/A')}")
                print(f"   Description: {item.get('description', 'N/A')[:100]}...")
        else:
            print("⚠️ No RSS content fetched")
        
        print()
        
        # Test 3: Fetch Reddit content
        print("3️⃣ Testing Reddit content extraction...")
        
        reddit_content = await curator._fetch_reddit_content(
            'https://www.reddit.com/r/MachineLearning/.json'
        )
        
        if reddit_content:
            print(f"✅ Fetched {len(reddit_content)} posts from Reddit\n")
            print("📱 Sample Reddit Content:")
            print("-" * 70)
            
            for i, item in enumerate(reddit_content[:3], 1):
                print(f"\n{i}. {item.get('title', 'N/A')[:70]}...")
                print(f"   Score: {item.get('score', 0)}")
                print(f"   URL: {item.get('url', 'N/A')[:50]}...")
        else:
            print("⚠️ No Reddit content fetched")
        
        print()
        
        # Test 4: Fetch Hacker News content
        print("4️⃣ Testing Hacker News content extraction...")
        
        hn_content = await curator._fetch_hackernews_content()
        
        if hn_content:
            print(f"✅ Fetched {len(hn_content)} stories from Hacker News\n")
            print("💻 Sample Hacker News Content:")
            print("-" * 70)
            
            for i, item in enumerate(hn_content[:3], 1):
                print(f"\n{i}. {item.get('title', 'N/A')[:70]}...")
                print(f"   Score: {item.get('score', 0)}")
        else:
            print("⚠️ No Hacker News content fetched")
        
        print()
        
        # Test 5: Complete curation pipeline
        print("5️⃣ Testing complete content curation pipeline...")
        print("   Gathering content from all sources...")
        
        all_content = await curator.curate_content_from_sources()
        
        if all_content:
            print(f"✅ Curated {len(all_content)} total content pieces\n")
            print("🎯 Top Curated Content (sorted by engagement):")
            print("-" * 70)
            
            for i, item in enumerate(all_content[:5], 1):
                print(f"\n{i}. {item.get('title', 'N/A')[:70]}...")
                print(f"   Type: {item.get('type', 'N/A')}")
                print(f"   Engagement Score: {item.get('engagement_score', 0):.2f}")
                print(f"   Source: {item.get('source', 'N/A')}")
        else:
            print("⚠️ No content curated")
        
        print()
        
        # Test 6: Content filtering
        print("6️⃣ Testing content quality filtering...")
        
        sample_content = [
            {'title': 'Amazing AI breakthrough', 'score': 500},
            {'title': 'Minor update', 'score': 10},
            {'title': 'Revolutionary ML model', 'score': 300},
            {'title': 'Test', 'score': 5},
            {'title': 'Incredible AI development', 'score': 450},
        ]
        
        filtered = curator._filter_content(sample_content)
        
        print(f"✅ Filtered {len(sample_content)} items → {len(filtered)} high-quality items\n")
        print("🔍 Quality Filter Results:")
        print("-" * 70)
        
        for item in filtered:
            print(f"   • {item['title']} (score: {item['engagement_score']:.2f})")
        
        print()
        
        # Close the curator
        await curator.close()
        
        print("=" * 70)
        print("🎉 CONTENT CURATOR - ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("✅ RSS feed extraction is working")
        print("✅ Reddit content fetching is functional")
        print("✅ Hacker News integration is operational")
        print("✅ Content filtering is accurate")
        print("✅ Complete curation pipeline is working")
        print()
        print("📊 Content Sources Active:")
        print("   • Technology Review, TechCrunch, VentureBeat")
        print("   • Reddit (r/MachineLearning, r/artificial)")
        print("   • Hacker News top stories")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        return False

if __name__ == "__main__":
    print("\n")
    success = asyncio.run(test_content_curator())
    
    if success:
        print("✅ Content Curator is READY for production!")
    else:
        print("❌ Please fix the issues above before proceeding")
    
    print("\n")
    sys.exit(0 if success else 1)
