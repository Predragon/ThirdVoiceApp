# The Third Voice - Sample Context Templates
# For every family that stays together 💚

import datetime
import json

def generate_sample_templates():
    """
    Generate sample conversation histories for new users
    Each template shows the power of The Third Voice in different contexts
    """
    
    # Base timestamp for consistent sample data
    base_time = datetime.datetime.now()
    
    sample_templates = {
        'contacts': {
            'Sarah (Co-parent)': {
                'context': 'coparenting',
                'history': [
                    {
                        "id": "sample_coparent_1",
                        "time": (base_time - datetime.timedelta(days=3)).strftime("%m/%d %H:%M"),
                        "type": "translate",
                        "original": "You're late AGAIN. Emma was asking where daddy is. Do you even care about her schedule?",
                        "result": "Sarah is expressing frustration about timing, but the real message is about Emma's emotional needs. She's worried about consistency for your daughter. A caring response acknowledging both the scheduling concern and Emma's feelings would help rebuild trust.",
                        "sentiment": "frustrated_but_caring",
                        "model": "Gemma 2 9B"
                    },
                    {
                        "id": "sample_coparent_2", 
                        "time": (base_time - datetime.timedelta(days=3, minutes=15)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "I got stuck at work, it's not like I wanted to be late. Emma knows I love her.",
                        "result": "I'm really sorry I was late - I got held up at work and should have called ahead. You're absolutely right that Emma needs consistency, and I can see how my lateness affected her. I love Emma deeply and want to do better with our schedule. Can we talk about how I can communicate better when delays happen?",
                        "sentiment": "improved",
                        "model": "Gemma 2 9B"
                    },
                    {
                        "id": "sample_coparent_3",
                        "time": (base_time - datetime.timedelta(days=1)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "Can I take Emma to the park this weekend? I want to make up for being late.",
                        "result": "Hi Sarah, I'd love to take Emma to the park this weekend - maybe Saturday afternoon? I've been thinking about our conversation and want to create more positive memories with her. Would that work with your plans? I'm committed to being more reliable with our schedule.",
                        "sentiment": "improved",
                        "model": "Llama 3.2 3B"
                    }
                ]
            },
            
            'Mom': {
                'context': 'family',
                'history': [
                    {
                        "id": "sample_family_1",
                        "time": (base_time - datetime.timedelta(days=5)).strftime("%m/%d %H:%M"),
                        "type": "translate",
                        "original": "I never hear from you anymore. I see other parents with their kids every week. I guess I'm not important.",
                        "result": "Your mom is feeling disconnected and lonely. Behind the guilt-inducing words is a mother who misses her child and wants to feel valued. She's comparing herself to other parents and feeling left out. A response that acknowledges her importance and suggests specific ways to connect would mean everything to her.",
                        "sentiment": "lonely_but_loving",
                        "model": "Phi 3 Mini"
                    },
                    {
                        "id": "sample_family_2",
                        "time": (base_time - datetime.timedelta(days=5, minutes=30)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "Mom, I'm just busy with work and stuff. You know I care about you.",
                        "result": "Mom, you're absolutely important to me and I'm sorry I haven't been staying in touch like I should. Work has been overwhelming, but that's no excuse for not making time for you. You mean the world to me. Can we set up a regular call time? Maybe Sunday evenings? I want to be better at this.",
                        "sentiment": "improved",
                        "model": "Phi 3 Mini"
                    },
                    {
                        "id": "sample_family_3",
                        "time": (base_time - datetime.timedelta(days=2)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "Thanks for the dinner you made last week. It was good.",
                        "result": "Mom, I've been thinking about that incredible dinner you made last week. Not just the food (which was amazing), but the love and effort you put into it. Those moments around your table remind me why family is everything. Thank you for always taking such good care of me, even as an adult. I love you.",
                        "sentiment": "improved",
                        "model": "Gemma 2 9B"
                    }
                ]
            },
            
            'Jessica (Wife)': {
                'context': 'romantic',
                'history': [
                    {
                        "id": "sample_romantic_1",
                        "time": (base_time - datetime.timedelta(days=7)).strftime("%m/%d %H:%M"),
                        "type": "translate",
                        "original": "Fine, do whatever you want. I'm tired of being the only one who cares about this relationship.",
                        "result": "Jessica is feeling emotionally exhausted and disconnected. 'Fine' doesn't mean she's okay - it means she's giving up fighting for your attention. She feels like she's putting in all the effort while you're disengaged. She needs reassurance that you still care and want to actively participate in rebuilding your connection.",
                        "sentiment": "exhausted_but_hopeful",
                        "model": "Llama 3.2 3B"
                    },
                    {
                        "id": "sample_romantic_2",
                        "time": (base_time - datetime.timedelta(days=7, minutes=45)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "I do care about us. I'm just stressed with everything going on.",
                        "result": "Jessica, I hear you saying you're tired of being the only one fighting for us, and you're right. I've been letting stress get in the way of showing you how much you mean to me. You deserve better than that. I do care deeply about our relationship, and I want to prove it through my actions, not just words. Can we talk about how I can be more present?",
                        "sentiment": "improved",
                        "model": "Llama 3.2 3B"
                    },
                    {
                        "id": "sample_romantic_3",
                        "time": (base_time - datetime.timedelta(days=4)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "I picked up your favorite coffee on my way home.",
                        "result": "I saw your favorite coffee at the café and couldn't resist getting it for you. It made me smile thinking about that look you get when you take the first sip. These little moments remind me how much joy you bring to my life. I love you, and I'm grateful for everything you do for us. ☕💕",
                        "sentiment": "improved",
                        "model": "Gemma 2 9B"
                    }
                ]
            },
            
            'David (Boss)': {
                'context': 'workplace',
                'history': [
                    {
                        "id": "sample_work_1",
                        "time": (base_time - datetime.timedelta(days=2)).strftime("%m/%d %H:%M"),
                        "type": "translate",
                        "original": "We need to talk about your performance lately. Your work isn't meeting expectations.",
                        "result": "David is addressing performance concerns, which likely stems from specific observations about your work quality or consistency. This is a professional conversation, not personal criticism. He's giving you an opportunity to understand expectations and improve. Responding with openness to feedback and questions about specific areas will show professionalism and commitment to growth.",
                        "sentiment": "professional_concern",
                        "model": "Phi 3 Mini"
                    },
                    {
                        "id": "sample_work_2",
                        "time": (base_time - datetime.timedelta(days=2, minutes=20)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "I've been dealing with some personal stuff but I'm trying my best at work.",
                        "result": "I appreciate you bringing this to my attention, David. I want to understand specifically which areas aren't meeting expectations so I can address them directly. I've had some personal challenges recently, but I'm committed to maintaining professional standards. Could we discuss specific goals and perhaps check in regularly so I can ensure I'm meeting your expectations?",
                        "sentiment": "improved",
                        "model": "Phi 3 Mini"
                    },
                    {
                        "id": "sample_work_3",
                        "time": (base_time - datetime.timedelta(days=1)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "I finished the Johnson report early. Should be good now.",
                        "result": "Hi David, I've completed the Johnson report ahead of schedule and incorporated the feedback from our previous discussion. I've double-checked the analysis and data accuracy. I'd appreciate your review when you have a chance, and I'm happy to make any adjustments needed. Thank you for your guidance - it's helping me improve my work quality.",
                        "sentiment": "improved",
                        "model": "Gemma 2 9B"
                    }
                ]
            },
            
            'Alex (Best Friend)': {
                'context': 'friend',
                'history': [
                    {
                        "id": "sample_friend_1",
                        "time": (base_time - datetime.timedelta(days=6)).strftime("%m/%d %H:%M"),
                        "type": "translate",
                        "original": "You've been weird lately. Always canceling plans, never returning calls. What's going on with you?",
                        "result": "Alex is worried about you and notices you've been distant. The direct approach shows he cares enough to confront the issue rather than just letting the friendship fade. He's giving you an opening to share what's really going on. Your friend is reaching out because he values your relationship and wants to understand how to support you.",
                        "sentiment": "concerned_caring",
                        "model": "Llama 3.2 3B"
                    },
                    {
                        "id": "sample_friend_2",
                        "time": (base_time - datetime.timedelta(days=6, minutes=35)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "Just got a lot going on right now. Nothing personal against you.",
                        "result": "You're right, Alex - I have been distant and I'm sorry. I've been dealing with some heavy personal stuff and haven't been great at staying connected with the people who matter most. It's not about you at all - you're one of the most important people in my life. Can we grab coffee this week? I'd like to talk and explain what's been going on.",
                        "sentiment": "improved",
                        "model": "Llama 3.2 3B"
                    },
                    {
                        "id": "sample_friend_3",
                        "time": (base_time - datetime.timedelta(hours=8)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "Thanks for listening yesterday. Felt good to talk.",
                        "result": "Alex, thank you for being such an incredible friend yesterday. Having someone who really listens without judgment means everything to me. You've always been there when I needed you, and I don't take that for granted. I'm lucky to have a friend like you in my corner. Let's grab those beers soon - my treat!",
                        "sentiment": "improved",
                        "model": "Gemma 2 9B"
                    }
                ]
            },
            
            'General': {
                'context': 'general',
                'history': [
                    {
                        "id": "sample_general_1",
                        "time": (base_time - datetime.timedelta(days=1)).strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": "Hey, can you call me back when you get this?",
                        "result": "Hi! I hope you're having a good day. Could you give me a call when you have a few minutes? I'd love to catch up and there's something I wanted to discuss with you. No rush - whenever works for you. Thanks!",
                        "sentiment": "improved",
                        "model": "Phi 3 Mini"
                    },
                    {
                        "id": "sample_general_2",
                        "time": (base_time - datetime.timedelta(hours=6)).strftime("%m/%d %H:%M"),
                        "type": "translate",
                        "original": "I'm fine, don't worry about me.",
                        "result": "When someone says 'I'm fine, don't worry about me,' they're often not fine at all. This is usually a protective response - they may be struggling but don't want to burden you, or they're testing if you'll persist in caring. The best response is gentle persistence, acknowledging their words while leaving the door open for deeper conversation.",
                        "sentiment": "guarded_but_needing_support",
                        "model": "Gemma 2 9B"
                    }
                ]
            }
        },
        
        'journal_entries': {
            'Sarah (Co-parent)': {
                'what_worked': 'Acknowledging her concerns about Emma first, then addressing the practical issues. Taking responsibility without getting defensive.',
                'what_didnt': 'Making excuses about work instead of focusing on the impact on Emma. Getting defensive about my intentions.',
                'insights': 'Sarah and I both want what\'s best for Emma. When I frame responses around Emma\'s needs, we communicate better.',
                'patterns': 'Sarah gets frustrated when she feels like she\'s managing everything alone. Clear communication about delays and genuine accountability helps a lot.'
            },
            
            'Mom': {
                'what_worked': 'Acknowledging her feelings and expressing appreciation for specific things she does. Setting up regular call times.',
                'what_didnt': 'Dismissing her concerns as guilt trips. Making generic statements about being busy.',
                'insights': 'Mom needs to feel valued and included in my life. Regular contact matters more than grand gestures.',
                'patterns': 'Mom communicates love through service and wants to feel needed. She compares herself to other parents and needs reassurance.'
            },
            
            'Jessica (Wife)': {
                'what_worked': 'Really listening to the emotion behind her words. Acknowledging my part in the problems. Small gestures with personal meaning.',
                'what_didnt': 'Minimizing her feelings or making it about my stress. Being defensive instead of understanding.',
                'insights': 'Jessica needs to feel like we\'re partners working together, not like she\'s managing the relationship alone.',
                'patterns': 'She withdraws when she feels unheard. "Fine" means she\'s giving up, not that she\'s okay.'
            },
            
            'David (Boss)': {
                'what_worked': 'Professional tone, asking for specific feedback, showing commitment to improvement. Following up on conversations.',
                'what_didnt': 'Bringing personal issues into work discussions. Being vague about my improvements.',
                'insights': 'David appreciates direct communication and proactive problem-solving. He wants to see growth, not just excuses.',
                'patterns': 'Clear expectations and regular check-ins work better than assuming everything is fine.'
            },
            
            'Alex (Best Friend)': {
                'what_worked': 'Being honest about my struggles instead of making excuses. Appreciating his support explicitly.',
                'what_didnt': 'Pushing him away when I needed support most. Being vague about what was going on.',
                'insights': 'True friends want to help, not judge. Alex values honesty and direct communication.',
                'patterns': 'Alex shows care by being direct and persistent. He doesn\'t give up on people he cares about.'
            },
            
            'General': {
                'what_worked': 'Adding warmth and context to requests. Reading between the lines when someone says they\'re "fine".',
                'what_didnt': 'Being too brief or impersonal in messages. Taking "I\'m fine" at face value.',
                'insights': 'Most communication is about connection, not just information. People need to feel heard and valued.',
                'patterns': 'Small changes in tone and approach can completely change how messages are received.'
            }
        },
        
        'user_stats': {
            'total_messages': 15,
            'coached_messages': 9,
            'translated_messages': 6
        },
        
        'feedback_data': {
            'sample_coparent_1': 'positive',
            'sample_coparent_2': 'positive',
            'sample_family_1': 'positive',
            'sample_family_2': 'positive',
            'sample_romantic_1': 'positive',
            'sample_romantic_2': 'positive',
            'sample_work_1': 'positive',
            'sample_work_2': 'positive',
            'sample_friend_1': 'positive',
            'sample_friend_2': 'positive',
            'sample_general_1': 'positive',
            'sample_general_2': 'positive'
        }
    }
    
    return sample_templates

def integrate_sample_templates_into_app():
    """
    Integration code to add to the main Streamlit app
    """
    
    integration_code = '''
    
# Add this function after your existing defaults setup
def load_sample_templates():
    """Load sample templates for new users"""
    return {
        'contacts': {
            'Sarah (Co-parent)': {
                'context': 'coparenting',
                'history': [
                    # ... (sample data from above)
                ]
            },
            # ... (all other sample contacts)
        },
        'journal_entries': {
            # ... (sample journal entries)
        },
        'user_stats': {
            'total_messages': 15,
            'coached_messages': 9,
            'translated_messages': 6
        },
        'feedback_data': {
            # ... (sample feedback data)
        }
    }

# Modify your session state initialization
defaults = {
    'token_validated': not REQUIRE_TOKEN,
    'api_key': st.secrets.get("OPENROUTER_API_KEY", ""),
    'contacts': {'General': {'context': 'general', 'history': []}},
    'active_contact': 'General',
    'journal_entries': {},
    'feedback_data': {},
    'user_stats': {'total_messages': 0, 'coached_messages': 0, 'translated_messages': 0},
    'sample_templates_loaded': False  # Add this new flag
}

# Add this after the defaults setup
if not st.session_state.get('sample_templates_loaded', False):
    # Check if user has any real data
    has_real_data = (
        len(st.session_state.contacts) > 1 or 
        len(st.session_state.contacts.get('General', {}).get('history', [])) > 0 or
        st.session_state.user_stats['total_messages'] > 0
    )
    
    if not has_real_data:
        # Load sample templates for new users
        sample_data = load_sample_templates()
        st.session_state.contacts = sample_data['contacts']
        st.session_state.journal_entries = sample_data['journal_entries']
        st.session_state.user_stats = sample_data['user_stats']
        st.session_state.feedback_data = sample_data['feedback_data']
        st.session_state.active_contact = 'Sarah (Co-parent)'  # Start with compelling example
        
        # Add welcome message
        st.session_state.show_welcome = True
    
    st.session_state.sample_templates_loaded = True

# Add this welcome message after the header
if st.session_state.get('show_welcome', False):
    st.info("""
    🎉 **Welcome to The Third Voice!** 
    
    We've loaded sample conversations to show you how it works. These examples demonstrate:
    - 💬 How to coach your messages before sending
    - 🔍 How to understand the real meaning behind what others say
    - 📊 How to track your communication growth
    
    Try exploring the different contacts and their histories, then start your own conversations!
    """)
    
    if st.button("Got it! Let's start communicating better"):
        st.session_state.show_welcome = False
        st.rerun()

# Add an option to clear sample data
if st.sidebar.button("🆕 Clear Sample Data & Start Fresh"):
    # Reset to defaults
    st.session_state.contacts = {'General': {'context': 'general', 'history': []}}
    st.session_state.active_contact = 'General'
    st.session_state.journal_entries = {}
    st.session_state.feedback_data = {}
    st.session_state.user_stats = {'total_messages': 0, 'coached_messages': 0, 'translated_messages': 0}
    st.session_state.show_welcome = False
    st.rerun()
    '''
    
    return integration_code

# Example usage and testing
if __name__ == "__main__":
    # Generate the sample templates
    templates = generate_sample_templates()
    
    # Save to JSON file for easy import
    with open('third_voice_sample_templates.json', 'w') as f:
        json.dump(templates, f, indent=2)
    
    print("✅ Sample templates generated successfully!")
    print(f"📊 Created {len(templates['contacts'])} sample contacts")
    print(f"💬 Total sample messages: {templates['user_stats']['total_messages']}")
    print(f"📝 Journal entries for {len(templates['journal_entries'])} relationships")
    
    # Print integration instructions
    print("\n🔧 Integration Instructions:")
    print("1. Add the load_sample_templates() function to your app")
    print("2. Add the session state initialization code")
    print("3. Add the welcome message code after your header")
    print("4. Add the clear sample data button to your sidebar")
    print("5. Your new users will now see compelling examples immediately!")
