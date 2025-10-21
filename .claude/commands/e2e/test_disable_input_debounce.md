# E2E Test: Input Disabling and Debouncing

Test input disabling during query execution and debouncing functionality in the Natural Language SQL Interface application.

## User Story

As a user  
I want the input area to be disabled while a query is processing  
So that I don't accidentally type or submit multiple queries at once

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** the query input textbox is enabled and can accept text
5. **Verify** the query button is enabled

6. Click "Upload Data" button to open the modal
7. Click on "Users Data" sample data button to load sample data
8. Wait for the data to be loaded
9. **Verify** the users table appears in the Available Tables section

10. Enter the query: "Show me all users"
11. Take a screenshot of the query input before execution
12. Click the Query button
13. Immediately after clicking (within 100ms):
    - **Verify** the query input textbox is disabled
    - **Verify** the query button is disabled and shows loading spinner
    - Try to type additional text in the query input
    - **Verify** no additional text can be entered
14. Take a screenshot showing the disabled state

15. Wait for the query to complete
16. **Verify** the query input textbox is re-enabled
17. **Verify** the query button is re-enabled and shows "Query" text
18. **Verify** the results are displayed
19. Take a screenshot of the re-enabled state with results

20. Test debouncing:
    - Enter a new query: "Count all users"
    - Rapidly click the Query button 5 times within 1 second
    - **Verify** only one query is executed (results should update once, not multiple times)
    - **Verify** no errors are shown

21. Test keyboard shortcut with disabled state:
    - Enter another query: "Show user names"
    - Press Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux)
    - **Verify** the input becomes disabled during execution
    - **Verify** the input is re-enabled after completion

## Success Criteria
- Query input is disabled during query execution
- Query button is disabled during query execution
- User cannot type in the textarea while a query is processing
- Input and button are re-enabled after query completion
- Debouncing prevents multiple rapid API requests
- Visual feedback is provided for disabled state
- 4 screenshots are taken