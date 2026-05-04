import apiClient from "./api.js";

export const albumService = {
    getAll() { return apiClient.get("/albums");},
    getPending() { return apiClient.get("/albums/pending"); },
    getPublic() { return apiClient.get("/albums/public"); },
    create(album) { return apiClient.post("/albums", album);},
    approve(id) { return apiClient.patch(`/albums/${id}/approve`);},
    reject(id) { return apiClient.patch(`/albums/${id}/reject`);}, 
    remove(id) { return apiClient.delete(`/albums/${id}`); }
}

export default albumService;
