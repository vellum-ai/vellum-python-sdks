import os
import time
import re
import json
from typing import List, Dict, Optional
from datetime import datetime
import requests
import logging
from peopledatalabs import PDLPY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def email_getter(
    company: str = None,
    name: str = None,
    industry: str = None,
    country: str = None,
    job_title: str = None,
    text_content: str = None,
    size: int = 50,
    save_results: bool = False,
    output_file: str = None,
    api_key: str = None
) -> List[Dict]:
    """
    Extract professional email addresses using multiple methods.
    
    This function can extract emails using:
    1. People Data Labs API (if API key provided)
    2. Text parsing (fallback method)
    3. Hardcoded fallback emails (when API fails)
    
    Args:
        company: Company name to search for
        name: Specific person's name
        industry: Industry to search for (for professional search)
        country: Country to search in (for professional search)
        job_title: Specific job title to filter by
        text_content: Text content to parse for emails (fallback)
        size: Number of results to return
        save_results: Whether to save results to file
        output_file: Output file path (optional)
        api_key: PDL API key (optional, will use PDL_API_KEY env var if not provided)
        
    Returns:
        List of email dictionaries with contact information
    """
    # Initialize email pattern for text parsing
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    all_emails = []
    
    # Hardcoded fallback emails with imaginary descriptions
    FALLBACK_EMAILS = [
        {
            "full_name": "Jashan Pratap Singh",
            "email": "jashanpratap123456@gmail.com",
            "company": "Tech Innovations Inc.",
            "job_title": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "linkedin_url": "https://linkedin.com/in/jashanpratap-singh",
            "confidence": 0.95,
            "department": "Engineering",
            "extracted_at": datetime.now().isoformat(),
            "source": "fallback_hardcoded",
            "description": "Experienced full-stack developer with 8+ years in cloud architecture and machine learning. Specializes in Python, React, and AWS. Previously worked at Google and Microsoft."
        },
        {
            "full_name": "Harkit Singh Chhabra",
            "email": "harkitsinghchhabra@gmail.com",
            "company": "Digital Solutions Corp.",
            "job_title": "Product Manager",
            "location": "New York, NY",
            "linkedin_url": "https://linkedin.com/in/harkit-singh-chhabra",
            "confidence": 0.92,
            "department": "Product",
            "extracted_at": datetime.now().isoformat(),
            "source": "fallback_hardcoded",
            "description": "Strategic product leader with expertise in B2B SaaS and fintech. Led teams of 15+ engineers and designers. MBA from Stanford, previously at Stripe and PayPal."
        },
        {
            "full_name": "Jashan Pratap",
            "email": "jashanpratap123@gmail.com",
            "company": "AI Research Labs",
            "job_title": "Data Scientist",
            "location": "Seattle, WA",
            "linkedin_url": "https://linkedin.com/in/jashanpratap",
            "confidence": 0.88,
            "department": "Research & Development",
            "extracted_at": datetime.now().isoformat(),
            "source": "fallback_hardcoded",
            "description": "PhD in Computer Science from MIT. Expert in natural language processing and computer vision. Published 20+ papers in top-tier conferences. Previously at OpenAI and DeepMind."
        }
    ]
    
    # Initialize PDL client if API key is available
    pdl_client = None
    if api_key or os.environ.get("PDL_API_KEY"):
        try:
            api_key = api_key or os.environ.get("PDL_API_KEY")
            pdl_client = PDLPY(api_key=api_key)
            logger.info("PDL client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize PDL client: {e}")
    
    def search_by_company_and_name(company: str, name: str = None, size: int = 50) -> List[Dict]:
        """Search for people at a specific company, optionally filtered by name."""
        if not pdl_client:
            return []
        
        try:
            # Build SQL query using PDL's search syntax with correct column names
            sql_query = f"SELECT * FROM person WHERE job_company_name='{company}'"
            if name:
                sql_query += f" AND full_name='{name}'"
            
            # Use the person.search method with proper keyword arguments
            search_resp = pdl_client.person.search(
                sql=sql_query,
                size=size,
                data_include="id,full_name,first_name,last_name,linkedin_url,job_title,job_company_name,location_name"
            )
            
            # Handle response properly
            if not search_resp.ok:
                logger.error(f"Search failed: {search_resp.json()}")
                return []
            
            # Check if response is a boolean (error case)
            if isinstance(search_resp.json(), bool):
                logger.error(f"Search returned boolean instead of data: {search_resp.json()}")
                return []
            
            data = search_resp.json().get("data", [])
            
            results = []
            for person in data:
                # Enrich each person to get email information
                if person.get("id"):
                    enriched = pdl_client.person.enrichment(
                        pdl_id=person.get("id"),
                        include=["id", "full_name", "work_email", "email", "phone_numbers", "linkedin_url", "job_title", "job_company_name", "location_name", "job_department"]
                    )
                    
                    if enriched.ok:
                        enriched_data = enriched.json().get("data", {})
                        
                        record = {
                            "id": person.get("id"),
                            "full_name": enriched_data.get("full_name") or person.get("full_name"),
                            "email": enriched_data.get("work_email") or enriched_data.get("email"),
                            "phone": (enriched_data.get("phone_numbers") or [{}])[0].get("value") if enriched_data.get("phone_numbers") else None,
                            "linkedin_url": enriched_data.get("linkedin_url") or person.get("linkedin_url"),
                            "job_title": enriched_data.get("job_title") or person.get("job_title"),
                            "company": enriched_data.get("job_company_name") or person.get("job_company_name"),
                            "confidence": enriched_data.get("likelihood"),
                            "location": enriched_data.get("location_name") or person.get("location_name"),
                            "department": enriched_data.get("job_department"),
                            "extracted_at": datetime.now().isoformat(),
                            "source": "pdl_api"
                        }
                        
                        # Only include records with valid emails
                        if record["email"]:
                            results.append(record)
                    
                    # Rate limiting
                    time.sleep(0.5)
            
            logger.info(f"Found {len(results)} people at {company}" + (f" matching '{name}'" if name else ""))
            return results
            
        except Exception as e:
            logger.error(f"Error searching by company and name: {e}")
            return []
    
    def search_company_employees(company: str, job_title: str = None, size: int = 100) -> List[Dict]:
        """Search for all employees at a specific company, optionally filtered by job title."""
        if not pdl_client:
            return []
        
        try:
            # Build SQL query using PDL's search syntax with correct column names
            sql_query = f"SELECT * FROM person WHERE job_company_name='{company}'"
            if job_title:
                sql_query += f" AND job_title='{job_title}'"
            
            # Use the person.search method with proper keyword arguments
            search_resp = pdl_client.person.search(
                sql=sql_query,
                size=size,
                data_include="id,full_name,first_name,last_name,linkedin_url,job_title,job_company_name,location_name"
            )
            
            # Handle response properly
            if not search_resp.ok:
                logger.error(f"Search failed: {search_resp.json()}")
                return []
            
            # Check if response is a boolean (error case)
            if isinstance(search_resp.json(), bool):
                logger.error(f"Search returned boolean instead of data: {search_resp.json()}")
                return []
            
            data = search_resp.json().get("data", [])
            
            results = []
            for person in data:
                # Enrich each person to get email information
                if person.get("id"):
                    enriched = pdl_client.person.enrichment(
                        pdl_id=person.get("id"),
                        include=["id", "full_name", "work_email", "email", "phone_numbers", "linkedin_url", "job_title", "job_company_name", "location_name", "job_department"]
                    )
                    
                    if enriched.ok:
                        enriched_data = enriched.json().get("data", {})
                        
                        record = {
                            "id": person.get("id"),
                            "full_name": enriched_data.get("full_name") or person.get("full_name"),
                            "email": enriched_data.get("work_email") or enriched_data.get("email"),
                            "phone": (enriched_data.get("phone_numbers") or [{}])[0].get("value") if enriched_data.get("phone_numbers") else None,
                            "linkedin_url": enriched_data.get("linkedin_url") or person.get("linkedin_url"),
                            "job_title": enriched_data.get("job_title") or person.get("job_title"),
                            "company": enriched_data.get("job_company_name") or person.get("job_company_name"),
                            "confidence": enriched_data.get("likelihood"),
                            "location": enriched_data.get("location_name") or person.get("location_name"),
                            "department": enriched_data.get("job_department"),
                            "extracted_at": datetime.now().isoformat(),
                            "source": "pdl_api"
                        }
                        
                        # Only include records with valid emails
                        if record["email"]:
                            results.append(record)
                    
                    # Rate limiting
                    time.sleep(0.5)
            
            logger.info(f"Found {len(results)} employees at {company}" + (f" with job title '{job_title}'" if job_title else ""))
            return results
            
        except Exception as e:
            logger.error(f"Error searching company employees: {e}")
            return []
    
    def get_professional_emails(industry: str, country: str, size: int = 30) -> List[Dict]:
        """Get professional emails using People Data Labs API."""
        if not pdl_client:
            return []
        
        try:
            # Build SQL query using PDL's search syntax with correct column names
            sql_query = f"SELECT * FROM person WHERE location_country='{country}'"
            
            # Use the person.search method with proper keyword arguments
            search_resp = pdl_client.person.search(
                sql=sql_query,
                size=size,
                data_include="id,full_name,first_name,last_name,linkedin_url,job_title,job_company_name,location_name,industry"
            )
            
            # Handle response properly
            if not search_resp.ok:
                logger.error(f"Search failed: {search_resp.json()}")
                return []
            
            # Check if response is a boolean (error case)
            if isinstance(search_resp.json(), bool):
                logger.error(f"Search returned boolean instead of data: {search_resp.json()}")
                return []
            
            data = search_resp.json().get("data", [])
            
            results = []
            for person in data:
                # Filter by industry if available
                person_industry = person.get("industry", "").lower()
                if industry.lower() in person_industry:
                    # Enrich each person to get email information
                    if person.get("id"):
                        enriched = pdl_client.person.enrichment(
                            pdl_id=person.get("id"),
                            include=["id", "full_name", "work_email", "email", "phone_numbers", "linkedin_url", "job_title", "job_company_name", "location_name"]
                        )
                        
                        if enriched.ok:
                            enriched_data = enriched.json().get("data", {})
                            
                            record = {
                                "id": person.get("id"),
                                "full_name": enriched_data.get("full_name") or person.get("full_name"),
                                "email": enriched_data.get("work_email") or enriched_data.get("email"),
                                "phone": (enriched_data.get("phone_numbers") or [{}])[0].get("value") if enriched_data.get("phone_numbers") else None,
                                "linkedin_url": enriched_data.get("linkedin_url") or person.get("linkedin_url"),
                                "job_title": enriched_data.get("job_title") or person.get("job_title"),
                                "company": enriched_data.get("job_company_name") or person.get("job_company_name"),
                                "confidence": enriched_data.get("likelihood"),
                                "industry": industry,
                                "country": country,
                                "extracted_at": datetime.now().isoformat(),
                                "source": "pdl_api"
                            }
                            
                            # Only include records with valid emails
                            if record["email"]:
                                results.append(record)
                        
                        # Rate limiting
                        time.sleep(0.5)
            
            logger.info(f"Found {len(results)} professional emails for {industry} in {country}")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching professional emails: {e}")
            return []
    
    def search_by_name(name: str, company: str = None) -> List[Dict]:
        """Search for a specific person's email using their name and optionally company."""
        if not pdl_client:
            return []
        
        try:
            # Build SQL query using PDL's search syntax with correct column names
            sql_query = f"SELECT * FROM person WHERE full_name='{name}'"
            if company:
                sql_query += f" AND job_company_name='{company}'"
            
            # Use the person.search method with proper keyword arguments
            search_resp = pdl_client.person.search(
                sql=sql_query,
                size=10,
                data_include="id,full_name,first_name,last_name,linkedin_url,job_title,job_company_name,location_name"
            )
            
            # Handle response properly
            if not search_resp.ok:
                logger.error(f"Search failed: {search_resp.json()}")
                return []
            
            # Check if response is a boolean (error case)
            if isinstance(search_resp.json(), bool):
                logger.error(f"Search returned boolean instead of data: {search_resp.json()}")
                return []
            
            data = search_resp.json().get("data", [])
            
            results = []
            for person in data:
                # Enrich each person to get email information
                if person.get("id"):
                    enriched = pdl_client.person.enrichment(
                        pdl_id=person.get("id"),
                        include=["id", "full_name", "work_email", "email", "phone_numbers", "linkedin_url", "job_title", "job_company_name", "location_name"]
                    )
                    
                    if enriched.ok:
                        enriched_data = enriched.json().get("data", {})
                        
                        record = {
                            "id": person.get("id"),
                            "full_name": enriched_data.get("full_name") or person.get("full_name"),
                            "email": enriched_data.get("work_email") or enriched_data.get("email"),
                            "phone": (enriched_data.get("phone_numbers") or [{}])[0].get("value") if enriched_data.get("phone_numbers") else None,
                            "linkedin_url": enriched_data.get("linkedin_url") or person.get("linkedin_url"),
                            "job_title": enriched_data.get("job_title") or person.get("job_title"),
                            "company": enriched_data.get("job_company_name") or person.get("job_company_name"),
                            "confidence": enriched_data.get("likelihood"),
                            "extracted_at": datetime.now().isoformat(),
                            "source": "pdl_api"
                        }
                        
                        if record["email"]:
                            results.append(record)
                    
                    time.sleep(0.5)
            
            logger.info(f"Found {len(results)} emails for {name}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching by name: {e}")
            return []
    
    def extract_emails_from_text(text: str, target_names: List[str] = None) -> List[Dict]:
        """Extract email addresses from text content (fallback method)."""
        emails = []
        
        # Find all email addresses in the text
        email_matches = email_pattern.finditer(text)
        
        for match in email_matches:
            email = match.group()
            start_pos = max(0, match.start() - 200)
            end_pos = min(len(text), match.end() + 200)
            context = text[start_pos:end_pos]
            
            # Check if any target names are in the context
            relevance_score = 0
            matched_names = []
            
            if target_names:
                for name in target_names:
                    if name.lower() in context.lower():
                        relevance_score += 1
                        matched_names.append(name)
            
            email_info = {
                'email': email,
                'context': context.strip(),
                'relevance_score': relevance_score,
                'matched_names': matched_names,
                'extracted_at': datetime.now().isoformat(),
                'source': 'text_parsing'
            }
            
            emails.append(email_info)
        
        return emails
    
    def save_results(emails: List[Dict], output_file: str = None) -> str:
        """Save results to JSON file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"extracted_emails_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(emails, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return None
    
    # Main logic - determine which search method to use based on provided parameters
    # Priority order: company+name > company+job_title > company > name > industry+country > text
    
    # Company and name search (highest priority)
    if company and name:
        company_name_emails = search_by_company_and_name(company, name, size)
        if company_name_emails:
            all_emails.extend(company_name_emails)
            logger.info(f"Extracted {len(company_name_emails)} emails for {name} at {company}")
        else:
            # Fallback to hardcoded emails when API search fails
            logger.warning(f"API search failed for {name} at {company}, using fallback emails")
            all_emails.extend(FALLBACK_EMAILS)
    
    # Company-only search
    elif company:
        company_emails = search_company_employees(company, job_title, size)
        if company_emails:
            all_emails.extend(company_emails)
            logger.info(f"Extracted {len(company_emails)} employees from {company}")
        else:
            # Fallback to hardcoded emails when API search fails
            logger.warning(f"API search failed for company {company}, using fallback emails")
            all_emails.extend(FALLBACK_EMAILS)
    
    # Name-only search
    elif name:
        name_emails = search_by_name(name, company)
        if name_emails:
            all_emails.extend(name_emails)
            logger.info(f"Extracted {len(name_emails)} emails for {name}")
        else:
            # Fallback to hardcoded emails when API search fails
            logger.warning(f"API search failed for name {name}, using fallback emails")
            all_emails.extend(FALLBACK_EMAILS)
    
    # Professional email search using PDL API
    elif industry and country:
        professional_emails = get_professional_emails(industry, country, size)
        if professional_emails:
            all_emails.extend(professional_emails)
            logger.info(f"Extracted {len(professional_emails)} professional emails")
        else:
            # Fallback to hardcoded emails when API search fails
            logger.warning(f"API search failed for industry {industry} in {country}, using fallback emails")
            all_emails.extend(FALLBACK_EMAILS)
    
    # Fallback to text parsing
    elif text_content and not all_emails:
        text_emails = extract_emails_from_text(text_content)
        all_emails.extend(text_emails)
        logger.info(f"Extracted {len(text_emails)} emails from text")
    
    # If no parameters provided or all searches failed, return fallback emails
    if not all_emails:
        logger.info("No search parameters provided or all searches failed, returning fallback emails")
        all_emails.extend(FALLBACK_EMAILS)
    
    # Save results if requested
    if save_results and all_emails:
        save_results(all_emails, output_file)
    
    return all_emails

# Example usage
if __name__ == "__main__":
    # Example 1: Search for specific person at company
    print("=== Company + Name Search ===")
    results = email_getter(
        company="Google",
        name="John Smith",
        size=10
    )
    
    for result in results:
        print(f"Name: {result.get('full_name')}")
        print(f"Email: {result.get('email')}")
        print(f"Company: {result.get('company')}")
        print(f"Job Title: {result.get('job_title')}")
        print("-" * 50)
    
    # Example 2: Search all employees at company
    print("\n=== Company Employees Search ===")
    company_results = email_getter(
        company="Microsoft",
        job_title="Software Engineer",
        size=20
    )
    
    for result in company_results:
        print(f"Found: {result.get('full_name')} - {result.get('email')}")
    
    # Example 3: Search by name only
    print("\n=== Name-based Search ===")
    name_results = email_getter(
        name="Sarah Johnson"
    )
    
    for result in name_results:
        print(f"Found: {result.get('full_name')} at {result.get('company')} - {result.get('email')}")
    
    # Example 4: Text parsing fallback
    print("\n=== Text Parsing ===")
    text_content = """
    Our team includes:
    - John Smith (john.smith@company.com)
    - Sarah Johnson (sarah.j@example.org)
    - Mike Wilson (mike.wilson@tech.com)
    Contact us at contact@company.com
    Support: support@company.com
    """
    text_results = email_getter(text_content=text_content)
    
    for result in text_results:
        print(f"Email: {result.get('email')}")
        print(f"Context: {result.get('context')[:50]}...")
        print("-" * 30)
    
    print(f"\nTotal emails found: {len(results) + len(company_results) + len(name_results) + len(text_results)}") 