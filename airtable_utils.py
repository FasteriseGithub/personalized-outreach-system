from pyairtable import Table

def icebreaker_post_to_airtable(icebreaker, prompt, gold_nuggets, lead_qualification_reasons, linkedin_profile_data, linkedin_link, email_address="None"):
    airtable_api_key = 'your_airtable_api_key'
    base_id = 'your_base_id'
    table_name = 'your_table_name'

    table = Table(airtable_api_key, base_id, table_name)

    data = {
        "Icebreaker": icebreaker,
        "Prompt": prompt,
        "Gold Nuggets": gold_nuggets,
        "Lead Qualification Reasons": lead_qualification_reasons,
        "Profile Data": linkedin_profile_data,
        "LinkedIn Link": linkedin_link,
        "Email": email_address
    }

    try:
        table.create(data)
        print("Icebreaker posted to Airtable successfully.")
    except Exception as e:
        print(f"Error posting icebreaker to Airtable: {e}")

def email_draft_post_to_airtable(email_draft, icebreaker, prompt, gold_nuggets, lead_qualification_reasons, linkedin_profile_data, linkedin_link, email_address):
    airtable_api_key = 'your_airtable_api_key'
    base_id = 'your_base_id'
    table_name = 'your_table_name'

    table = Table(airtable_api_key, base_id, table_name)

    data = {
        "Email Draft": email_draft,
        "Prompt": prompt,
        "LinkedIn Link": linkedin_link,
        "Email": email_address
    }

    try:
        table.create(data)
        print("Email draft posted to Airtable successfully.")
    except Exception as e:
        print(f"Error posting email draft to Airtable: {e}")