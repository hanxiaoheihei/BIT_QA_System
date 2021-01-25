import axios from 'axios';
import { API_HOST } from '../config.json';

export function sendMessage(sender, message) {
  return axios.post(`${API_HOST}/chat`, { sender, message });
}

export function uploadDoc(title, text) {
  const newText = text.replace(/\s/g, '');
  return axios.post(`${API_HOST}/doc`, { title, text: newText });
}

export function fetchDocs() {
  return axios.get(`${API_HOST}/doc`);
}

export function removeDoc(_id) {
  return axios.delete(`${API_HOST}/doc`, { data: { _id } });
}

export function fetchFaqs() {
  return axios.get(`${API_HOST}/faq`);
}

export function docAsk(_id, query) {
  return axios.post(`${API_HOST}/doc_qa`, { _id, query });
}
