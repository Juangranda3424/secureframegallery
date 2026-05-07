import apiClient from "./api.js";

export const notificationService = {
    list() {
        return apiClient.get("/notifications");
    },
    unread() {
        return apiClient.get("/notifications/unread");
    },
    markRead(id) {
        return apiClient.patch(`/notifications/${id}/read`);
    }
};

export default notificationService;
