#!/usr/bin/env python3
import re
import yaml
import os
import subprocess

# Function to validate the S3 bucket prefix when combined with the account ID.
def is_valid_bucket_prefix(prefix, account_id):
    """
    Validate that the full bucket name (prefix + '-' + account_id) adheres to S3 bucket naming rules.
    """
    full_bucket_name = f"{prefix}-{account_id}"
    
    # Check length: full bucket name must be between 3 and 63 characters.
    if not (3 <= len(full_bucket_name) <= 63):
        print(f"Error: Full bucket name '{full_bucket_name}' must be between 3 and 63 characters.")
        return False

    # Bucket name must be all lowercase.
    if full_bucket_name != full_bucket_name.lower():
        print("Error: Bucket name must be lowercase.")
        return False

    # Must start and end with a letter or number, and can only contain lowercase letters, numbers, hyphens, and periods.
    if not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', full_bucket_name):
        print("Error: Bucket name must start and end with a letter or number and may only contain lowercase letters, numbers, hyphens, and periods.")
        return False

    # Bucket name should not be formatted as an IP address.
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', full_bucket_name):
        print("Error: Bucket name must not be formatted as an IP address.")
        return False

    return True

# Simulated retrieval of AWS Account ID (in a real scenario, you could retrieve this via Boto3)
account_id = "123456789012"  # Replace with actual retrieval if needed.

# Prompt the user for input with validation on the bucket prefix.
while True:
    bucket_prefix = input("Enter the bucket name prefix: ").strip()
    if is_valid_bucket_prefix(bucket_prefix, account_id):
        break
    print("Please enter a valid bucket name prefix.")

# Prompt for region selection.
region_choice = input("Choose region (Enter 'E' for us-east-1 or 'W' for us-west-2): ").strip().upper()
region = "us-east-1" if region_choice == "E" else "us-west-2"

# Prompt for versioning preference.
versioning_input = input("Enable versioning? (yes/no): ").strip().lower()
versioning = "Enabled" if versioning_input in ["yes", "y"] else "Suspended"

# Path to the CloudFormation template.
template_path = "s3-versioning.yml"

# Load the existing YAML template.
with open(template_path, "r") as file:
    data = yaml.safe_load(file)

# Update the Parameters section with default values from user input.
# These Default values will be used by our deploy.yml workflow.
data["Parameters"]["BucketName"]["Default"] = bucket_prefix
data["Parameters"]["Region"]["Default"] = region
data["Parameters"]["VersioningStatus"]["Default"] = versioning

# Save the updated YAML file.
with open(template_path, "w") as file:
    yaml.dump(data, file, default_flow_style=False)

print("\nUpdated s3-versioning.yml with the following settings:")
print(f"  BucketName Default: {bucket_prefix}")
print(f"  Region Default: {region}")
print(f"  VersioningStatus Default: {versioning}")

# Optional: Commit and push changes to GitHub.
commit_choice = input("\nWould you like to commit and push these changes to GitHub? (yes/no): ").strip().lower()
if commit_choice in ["yes", "y"]:
    subprocess.run(["git", "add", template_path])
    subprocess.run(["git", "commit", "-m", "Updated s3-versioning.yml with user inputs from s3_setup.py"])
    subprocess.run(["git", "push", "origin", "main"])
    print("Changes have been committed and pushed.")
else:
    print("Changes not committed. You can push them later manually.")
