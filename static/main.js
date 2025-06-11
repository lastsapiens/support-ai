document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
  
    if (loginForm) {
      loginForm.addEventListener("submit", function (e) {
        e.preventDefault();
  
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
  
        fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
          })
            .then(res => {
              if (!res.ok) throw new Error("Invalid credentials");
              return res.json();
            })
            .then(data => {
              localStorage.setItem("access_token", data.access_token);
          
              fetch("http://127.0.0.1:8000/dashboard", {
                headers: { "Authorization": `Bearer ${data.access_token}` }
              })
                .then(res => res.json())
                .then(user => {
                  if (user.role === "responder") {
                    window.location.href = "/static/responder-dashboard.html";
                  } else {
                    window.location.href = "/static/dashboard.html";
                  }
                });
            })
            .catch(err => {
              document.getElementById("error").textContent = "Login failed: " + err.message;
            });
      });
    }
  
    const token = localStorage.getItem("access_token");
    if (!token) return;
  
    window.logout = function () {
      localStorage.removeItem("access_token");
      window.location.href = "/";
    };
  
    if (document.getElementById("ticket-form")) {
      // User dashboard logic
  
      fetch("http://127.0.0.1:8000/dashboard", {
        headers: { "Authorization": `Bearer ${token}` }
      })
        .then(res => {
          if (!res.ok) throw new Error("Unauthorized");
          return res.json();
        })
        .then(data => {
            document.getElementById("user-info").textContent = "Logged in as: " + data.username;
        })
        .catch(() => {
          alert("Session expired. Redirecting to login.");
          logout();
        });
  
      function fetchTickets() {
        fetch("http://127.0.0.1:8000/tickets/", {
          headers: { "Authorization": `Bearer ${token}` }
        })
          .then(res => res.json())
          .then(tickets => {
            const container = document.getElementById("tickets-list");
            container.innerHTML = "";
            if (!tickets || tickets.length === 0) {
              container.textContent = "No tickets found.";
              return;
            }
            tickets.forEach(t => {
              container.innerHTML += `
                <div class="ticket-card">
                  <strong>${t.title}</strong><br/>
                  <p>${t.description}</p>
                  <p><em>Status:</em> ${t.status} | <em>Priority:</em> ${t.priority} | <em>Category:</em> ${t.category || 'N/A'}</p>
                  <p><em>Wing:</em> ${t.wing || 'N/A'} | <em>Section:</em> ${t.section || 'N/A'}</p>
                  ${t.attachment_url ? `<p><a href="${t.attachment_url}" target="_blank">View Attachment</a></p>` : ''}
                  <small>Created at: ${new Date(t.created_at).toLocaleString()}</small>
                </div>
              `;
            });
          })
          .catch(() => {
            document.getElementById("tickets-list").textContent = "Failed to load tickets.";
          });
      }
  
      fetchTickets();
  
      document.getElementById("ticket-form").addEventListener("submit", function (e) {
        e.preventDefault();
  
        const formData = new FormData();
        formData.append("title", document.getElementById("title").value.trim());
        formData.append("description", document.getElementById("description").value.trim());
        formData.append("priority", document.getElementById("priority").value);
        formData.append("category", document.getElementById("category").value.trim());
        formData.append("wing", document.getElementById("wing").value.trim());
        formData.append("section", document.getElementById("section").value.trim());
  
        const fileInput = document.getElementById("attachment");
        if (fileInput.files.length > 0) {
          formData.append("attachment", fileInput.files[0]);
        }
  
        fetch("http://127.0.0.1:8000/tickets/", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`
          },
          body: formData
        })
          .then(res => {
            if (!res.ok) throw new Error("Failed to create ticket");
            return res.json();
          })
          .then(ticket => {
            alert("Ticket created!");
            document.getElementById("ticket-form").reset();
            fetchTickets();
          })
          .catch(err => alert(err.message));
      });
    }
  
    if (document.getElementById("responder-tickets-list")) {
      // Responder dashboard logic
  
      fetch("http://127.0.0.1:8000/dashboard", {
        headers: { "Authorization": `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
            document.getElementById("responder-info").textContent = "Logged in as: " + data.username;
        });
  
      fetch("http://127.0.0.1:8000/responder-dashboard", {
        headers: { "Authorization": `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(tickets => {
          const list = document.getElementById("responder-tickets-list");
          list.innerHTML = "";
          if (tickets.length === 0) {
            list.textContent = "No tickets available.";
            return;
          }
  
          tickets.forEach(t => {
            const ticketCard = document.createElement("div");
            ticketCard.className = "ticket-card";
            ticketCard.innerHTML = `
              <strong>${t.title}</strong><br/>
              <p>${t.description}</p>
              <p><em>Status:</em> ${t.status} | <em>Priority:</em> ${t.priority}</p>
              <p><em>Wing:</em> ${t.wing} | <em>Section:</em> ${t.section}</p>
              ${t.attachment_url ? `<p><a href="${t.attachment_url}" target="_blank">View Attachment</a></p>` : ''}
              <button class="assign-button" data-id="${t.id}">Assign to Me</button>
            `;
            list.appendChild(ticketCard);
          });
  
          document.querySelectorAll(".assign-button").forEach(btn => {
            btn.addEventListener("click", function () {
              const ticketId = this.getAttribute("data-id");
              fetch(`http://127.0.0.1:8000/tickets/${ticketId}/assign`, {
                method: "PUT",
                headers: {
                  "Authorization": `Bearer ${token}`
                }
              })
                .then(res => res.json())
                .then(() => {
                  alert("Ticket assigned to you.");
                  location.reload();
                })
                .catch(() => alert("Failed to assign ticket."));
            });
          });
        });
    }
  });
  