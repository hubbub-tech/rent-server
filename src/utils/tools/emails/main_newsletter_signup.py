def get_newsletter_welcome(newsletter_data):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    email_body_formatter.preview = f"New newsletter signup '{newsletter_data['email']}' {date.today().strftime('%B %-d, %Y')} - "

    email_body_formatter.user = "Hubbub Team"

    email_body_formatter.introduction = "New signup in town! Check it below."

    email_body_formatter.content = f"""
        <p>New Name: <bold>{newsletter_data['name']}</bold></p>
        <p>New Email: <bold>{newsletter_data['email']}</bold></p>
        """

    email_body_formatter.conclusion = "Thanks!"

    body = email_body_formatter.build()

    email_data.subject = "[Internal] New Newsletter Signup"
    email_data.to = (SG.DEFAULT_RECEIVER,)
    email_data.body = body
    return email_data
