import apiClient from "./api.js";

export const imageService = {
    list(albumId) { return apiClient.get(`/albums/${albumId}/images`);},
    listPublic(albumId) { return apiClient.get(`/albums/${albumId}/images/public`);},
    listQuarantine() { return apiClient.get("/albums/quarantine");},
    upload(albumId, file){
        const fd = new FormData(); 
        fd.append('file', file);
        return apiClient.post(`/albums/${albumId}/images`, fd, { headers: {'Content-Type':'multipart/form-data'}
        });
    },
    approve(imageId) { return apiClient.patch(`/albums/quarantine/${imageId}/approve`);},
    rejectQuarantine(imageId) { return apiClient.delete(`/albums/quarantine/${imageId}/reject`);},
    remove(albumId, imageId) { return apiClient.delete(`/albums/${albumId}/images/${imageId}`);}
};

export default imageService;
