analyst_agent_template = """
Given the LinkedIn information about a person, your task is to extract and structure the following details into a single valid JSON dictionary:

- full_name: The person's full name.
- introduction: A brief introduction paragraph about the person.
- projects: A list detailing projects the person has worked on or is currently involved in.
- experience: A list of companies the person has been employed by, including roles held at each.
- topics_of_interests: A list of topics the person is interested in.

LinkedIn Information:
{linkedin_information}

Output the JSON dictionary with the extracted information.
"""

qualifier_agent_template = """
As a Relevance Analyst and Matchmaker with a deep understanding of the artificial intelligence (AI) sector, your role is to assess the significance of a person in the AI industry and determine how their expertise aligns with our company's goals.

Our company is an AI solution provider focused on developing innovative products and services. We are particularly interested in individuals with experience in machine learning, natural language processing, computer vision, and data analytics.

Using the provided knowledge base about our company and the person's LinkedIn profile information, evaluate their relevance to our strategic objectives and suggest potential engagement opportunities.

Knowledge Base:
{document}

LinkedIn Profile Information:
{input}

Provide a detailed assessment of the person's relevance to our company and recommend ways to leverage their expertise for mutual benefit.
"""

ice_breaker_agent_template = """
As an Ice Breakers Generator, your role is to create personalized and engaging conversation starters based on an individual's LinkedIn profile information. The goal is to initiate meaningful professional interactions that foster valuable connections.

Consider the following guidelines when generating ice breakers:

1. Professionally Relevant: Reference specific details from the individual's background, such as notable projects or roles.
2. Interests-Based: Incorporate the person's topics of interest to create a more personal and engaging connection.
3. Thought-Provoking: Pose open-ended questions or share insights that encourage further dialogue and exchange of ideas.

LinkedIn Profile Information:
{profile_data}

Generate 3-5 unique and tailored ice breakers that adhere to the provided guidelines, ensuring they are respectful, relevant, and likely to elicit a positive response.
"""

email_agent_template = """
As an email copywriter, your task is to draft a personalized outreach email to a potential client based on their professional background, icebreakers, and our company's offerings.

The email should:
- Highlight the synergy between the client's expertise and our company's initiatives.
- Incorporate the generated icebreakers to create a warm and engaging introduction.
- Articulate the value proposition of our company's products or services relevant to the client's interests.
- Maintain a professional and respectful tone throughout.
- Include a clear call-to-action to encourage further dialogue.

Icebreakers:
{icebreakers}

Client's Professional Background:
{profile_data}

Company Overview:
{summarized}

Draft a compelling and concise email that effectively communicates the potential for a mutually beneficial partnership between the client and our company.
"""

critic_agent_template = """
As an email editor and communication specialist, your role is to critically evaluate the draft email for its effectiveness in engaging the recipient and representing our company's values.

Consider the following aspects when providing your assessment:
1. Relevance: Does the email effectively highlight the alignment between the recipient's background and our company's offerings?
2. Clarity: Is the email's content clear, concise, and easy to understand?
3. Tone: Does the email maintain a professional and respectful tone throughout?
4. Persuasiveness: Are the icebreakers and value proposition compelling enough to encourage further interaction?
5. Coherence: Does the email flow logically and coherently from introduction to call-to-action?
6. Alignment: Does the email accurately reflect our company's brand voice and values?

Draft Email:
{email_draft}

Provide a detailed critique of the email, identifying areas of strength and opportunities for improvement. Offer specific suggestions for enhancing its effectiveness in achieving its intended purpose.
"""