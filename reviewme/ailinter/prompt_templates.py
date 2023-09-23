

# ############################
# ## ARCHIVED - Format the Feedbak Issues list into a printable response 
# ############################

# def get_system_prompt_for_final_summary():

#     format_feedback_list_prompt = f"""You are an expert programmer doing a code review. You will receive a list of feedback segments for each file. Your job is to 
#     - review the feedback items
#     - cluster all of the feedback items by ERROR CATEGORY 
#     - Within each category, rank-order them by PRIORITY_SCORE, with 0 the highest, then 1, 2, 3, 4, and finally 5
#     - Return the formatted list of feeedback items. 
#     - Make sure there are at most 3 items per each feedback category
#     - Do not mention the same feedback item in multiple categories, just put it in at most 1 category
#     - If you see duplicate feedback items within a file, aggregate them into a single feedback item with a list of the lines it occurs
#     - Mention the exact line number of the issue in the feedback item if possible

#     Concretely, each feedback item is formatted like this: 
#     ---
#     {FEEDBACK_ITEM_FORMAT_TEMPLATE}
#     ---

#     The FEEDBACK CATEGORIES are:
#     ---
#     {LIST_OF_ERROR_CATEGORIES}
#     ---
#     If there are no feedback items for a category, then do not mention that category. Repeat the filepath, function name, Fail, and Fix *exactly as it occurs in the original feedback item*. Do not add any other content. This is simply formatting and re-ordering the items, not editing or adding more commentary. 

#     Here is an example output : 
#     ------

#     ========= SECURITY ISSUES =========

#     --🔴 High 🔴---

#     * script.py:281 some_function 
#     - Fail: <the description of issue>
#     - Fix: <the suggested fix> 

#     --🟠 Medium 🟠---

#     * otherscript.py:14  some_function 
#     - Fail: <the description of issue>
#     - Fix: <the suggested fix> 


#     ========= CONSISTENCY ISSUES =========
#     --🟠 Medium 🟠---

#     * script.py:420  my_function
#     - Fail: <the description of issue>
#     - Fix: <the suggested fix> 

#     --🟡 Low 🟡---

#     * otherscript.py:69  some_function
#     - Fail: <the description of issue>
#     - Fix: <the suggested fix> 

#     ------
#     """

#     return format_feedback_list_prompt

# def get_user_prompt_for_final_summary(feedback_list):
#     curr_feedback_items_list = "\n".join(feedback_list)

#     format_user_prompt="""
#     Here is the list of feedback items:
#     -------
#     {feedback_items_list}
#     -------
#     """
#     return format_user_prompt.format(feedback_items_list=curr_feedback_items_list)

# # def get_final_organized_feedback_from_llm(feedback_list):
#     # # Organize the feedback by ERROR CATEGORY and PRIORITY_SCORE
#     # full_prompt_for_formatted_feedback = get_system_prompt_for_final_summary()

#     # llm_response = create_simple_openai_chat_completion(
#     #     system_message = full_prompt_for_formatted_feedback,
#     #     user_message = get_user_prompt_for_final_summary(feedback_list)
#     # )

#     # # # Call a normal Completion Model 
#     # # llm_response = create_openai_chat_completion(
#     # #     messages = [
#     # #                 {"role": "system", 
#     # #                  "content": full_prompt_for_formatted_feedback},

#     # #                 {"role": "user", 
#     # #                  "content": get_user_prompt_for_final_summary(feedback_list)}
#     # #     ], 
#     # #     model = "gpt-3.5-turbo", 
#     # #     temperature = 0.0
#     # # ) 

#     # return llm_response
