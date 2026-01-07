# Django Admin Filters: Why They Appear

All sidebar filters in the Django Admin for the Plan model are auto-generated from the `list_filter` attribute of the `PlanAdmin` class. This is standard Django behavior and ensures that filters for status, category, type, bedrooms, and other fields are always available for quick data segmentation. No custom or hidden logic is used—what you see in the sidebar is a direct reflection of the fields listed in `list_filter`.

- **Purpose:** To allow fast filtering and segmentation of plans by key attributes.
- **How it works:** Django inspects the `list_filter` tuple and generates a filter UI for each field.
- **Guarantee:** All filters are visible and functional as long as they are present in `list_filter`.

*This documentation is for admin reference and should be preserved for future maintainers.*
