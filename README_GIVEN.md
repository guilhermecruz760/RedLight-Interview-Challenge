# 🏅 Redlight Sports Events Platform

In this challenge we expect you to **implement** a web platform to plan and manage sports events within Redlight 🏅

The aim of this challenge is to build a web platform that helps organize internal sports activities, allowing Redlight employees to create and join events while enabling admins to manage them efficiently.

### ✅ Requirements

This web platform should allow the user to:

- Create new sports events (e.g., Football Matches, Ping Pong Tournament)
- List existing events
- Show details of an existing event
- Update an existing event
- Delete an existing event
- Search for events
- Register participants (employees) to events
- List participants of a given event
- Mark an event as completed or cancelled
- User authentication 
- Make the mentioned entities soft deletable

### 🧩 Phases

##### 🎨 The frontend

On the frontend phase we want to see web pages where you can complete the goals established before. That is, create, list, search, update, and delete both events and participants.

Feel free to use any CSS frameworks like **Tailwind**, **Bootstrap**, or any similar one if you are familiar with it. If you want a challenge you can also try to finish this step using any web framework such as **React**, **Angular** or **VueJS**.

##### 🛠️ The backend

For the backend you should develop a server that responds to the frontend requests and integrates with a database that stores the information about the events and participants.

Here you're also free to use any backend technology you're familiar with, be it **Ruby on Rails**, **.NET**, **Django**, **ExpressJS**, or any other of your choosing. For database technologies you can achieve this either using relational databases such as **PostgreSQL** and **MySQL** or by using non-relational databases such as **MongoDB**.

##### ✨ Some extras

Once the application allows the user to perform the main goals, you can also develop the following extras:
- Define different user roles such as:
  - **Admin**: can create, update and delete events (owned and created by other users) and participants
  - **Participant**: can browse, register for events, create and manage their own events and view participants
- Prevent overbooking of events (do not allow more participants than the maximum allowed)
- Add filters for sport type, location, or date
- Allow users to upload pictures for their owned events
- Add simple email notifications for event registration (mock or real)
- Add the option to export events to a calendar format (.ics or Google Calendar)

##### 💡 Tips

Take advantage of your strengths. This challenge is intentionally open-ended to allow you to highlight the areas where you feel most confident and experienced. If you are more comfortable with building clean and intuitive user interfaces, invest in making the frontend polished, responsive, and easy to use. On the other hand, if your strength lies in API design or implementing backend logic, then focus on building a solid backend with clear, maintainable code and good architectural practices.

The goal is to demonstrate your ability to prioritize, make decisions, and deliver a working solution that solves the problem efficiently.

### 📝 Notes

An event is composed of:

- title  
- description  
- location  
- date and time  
- sport type (e.g., football, tennis, lacrosse 🧐, cheese rolling 🧀)  
- maximum number of participants  
- current status (enum: planned, completed, cancelled)  
- list of participants  
- picture (optional)

Example:

- title: Futebolada  
- description: Friendly 5-a-side game  
- location: Casa do pessoal dos HUC  
- date and time: 2025-07-20 18:00  
- sport type: Football  
- max participants: 10  
- status: Planned  
- participants: Cristiano Ronaldo, Luís Figo, Marinho, etc.

A participant is composed of:

- name  
- email  
- age (optional)  
- photo (optional)

Example:

- name: Cristiano Ronaldo  
- email: sou.lindo@cr7.pt  
- age: 40

---

### 📦 Delivery 

**Consider adding a README.md file to the project with documentation on how to set up and run the project when testing it.**

**Also add a short text (max. 2 pages) explaining how you structured the project, the development decisions you made, and the reasoning behind your choices during implementation and testing.**

When you're done, you should fork this repository and upload your work there to share it with us. Please try to share your process going through the steps you took to reach your final version.
