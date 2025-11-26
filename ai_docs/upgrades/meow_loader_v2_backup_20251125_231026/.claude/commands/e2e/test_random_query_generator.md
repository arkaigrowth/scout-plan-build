# E2E Test: Random Query Generator

Test the random query generation functionality in the Natural Language SQL Interface application.

## User Story

As a user  
I want to generate random natural language queries based on my database tables  
So that I can discover interesting insights from my data and see example queries that work with my specific schema

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** the Generate Random Query button is present
5. **Verify** the button is positioned on the right side of the query controls

### Test with No Data
6. Click the Generate Random Query button (without any data loaded)
7. **Verify** the query input field is populated with "Please upload some data first to generate queries."
8. Take a screenshot of the message

### Test with Sample Data
9. Click the Upload Data button
10. Click on the "Users Data" sample button
11. **Verify** the users table appears in Available Tables
12. Take a screenshot of the tables section
13. Click the Generate Random Query button
14. **Verify** the query input field is populated with a natural language query
15. **Verify** the generated query is relevant to the users table (e.g., contains references to users, signup dates, etc.)
16. Take a screenshot of the generated query
17. Click the Query button to execute the generated query
18. **Verify** the query executes successfully
19. **Verify** the SQL translation is displayed
20. **Verify** the results table contains data
21. Take a screenshot of the results

### Test Multiple Generations
22. Click the Generate Random Query button again
23. **Verify** a new, different query is generated
24. **Verify** the new query overwrites the previous content in the input field
25. Take a screenshot of the new generated query

## Success Criteria
- Generate Random Query button is visible and properly positioned
- Button generates appropriate messages when no data is loaded
- Button generates contextually relevant queries when data is loaded
- Generated queries are limited to two sentences maximum
- Generated queries can be executed successfully
- Button overwrites existing query input content
- Multiple clicks generate different queries
- 6 screenshots are taken