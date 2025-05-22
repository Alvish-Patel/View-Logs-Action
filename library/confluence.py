from plugins.confluence.restart import restart_all_confluence_instances, choose_profile


def perform_restart():
    profile_name = choose_profile()  # <- Prompt for profile here
    print("\n🔁 Restarting Confluence EC2 Instances via AWS Tag\n")
    tag_value = input("Enter instance tag value to match (default: 'confluence'): ").strip() or "confluence"
    restart_all_confluence_instances(profile_name, tag_value)


def run():
    perform_restart()