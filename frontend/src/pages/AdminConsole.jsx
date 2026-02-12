import React, { useState, useEffect } from 'react';
import { api, authHeaders } from '../services/api';
import { useTranslation } from 'react-i18next';

const AdminConsole = () => {
    const { t } = useTranslation();
    const [activity, setActivity] = useState([]);
    const [users, setUsers] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            const config = { headers: authHeaders() };

            try {
                const [activityRes, usersRes] = await Promise.all([
                    api.get('/admin/activity', config),
                    api.get('/admin/users', config)
                ]);
                setActivity(activityRes.data);
                setUsers(usersRes.data);
            } catch (err) {
                console.error('Failed to fetch admin data', err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleFileChange = (event) => {
        const file = event.target.files?.[0];
        setSelectedFile(file || null);
        setUploadStatus('');
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setUploadStatus('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            setUploading(true);
            setUploadStatus('Uploading document...');
            const config = {
                headers: {
                    ...authHeaders(),
                    'Content-Type': 'multipart/form-data'
                }
            };
            const response = await api.post('/documents/upload', formData, config);
            setUploadStatus(response.data?.message || 'Document uploaded successfully.');
        } catch (error) {
            const message = error?.response?.data?.detail || 'Upload failed.';
            setUploadStatus(typeof message === 'string' ? message : 'Upload failed.');
        } finally {
            setUploading(false);
        }
    };

    if (loading) return <div className="p-8 text-slate-400">Loading admin console...</div>;

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">{t('admin.title')}</h1>
                <p className="text-sm text-slate-500 mt-1">Monitor system-wide activity and manage user access.</p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-4">{t('admin.uploadDocument')}</h3>
                <div className="flex items-center gap-3">
                    <input
                        type="file"
                        accept=".pdf,.docx,.txt"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-slate-700 file:mr-4 file:rounded-md file:border-0 file:bg-slate-100 file:px-4 file:py-2 file:text-sm file:font-semibold"
                    />
                    <button
                        onClick={handleUpload}
                        disabled={uploading || !selectedFile}
                        className="px-4 py-2 bg-red-900 text-white rounded-md text-sm font-semibold disabled:opacity-50"
                    >
                        {uploading ? t('common.loading') : t('admin.uploadDocument')}
                    </button>
                </div>
                {uploadStatus ? <p className="mt-3 text-xs text-slate-600">{uploadStatus}</p> : null}
            </div>

            <div className="grid grid-cols-3 gap-8">
                <div className="col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                    <div className="p-6 border-b border-slate-50 flex items-center justify-between">
                        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">{t('admin.systemActivity')}</h3>
                    </div>
                    <div className="divide-y divide-slate-50">
                        {activity.map((act, i) => (
                            <div key={i} className="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors">
                                <div className="flex items-center space-x-4">
                                    <div className="w-10 h-10 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 capitalize">
                                        {act.user[0]}
                                    </div>
                                    <div>
                                        <div className="text-sm font-bold text-slate-900">{act.chat_title}</div>
                                        <div className="text-[10px] font-bold text-slate-400 uppercase">User: {act.user}</div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xs font-bold text-red-800">{act.message_count} Messages</div>
                                    <div className="text-[10px] text-slate-400">{new Date(act.created_at).toLocaleString()}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 overflow-hidden">
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-6">{t('admin.userManagement')}</h3>
                    <div className="space-y-4">
                        {users.map((user) => (
                            <div key={user.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                                <div className="flex items-center space-x-3">
                                    <div className={`w-2 h-2 rounded-full ${user.is_admin ? 'bg-red-800' : 'bg-green-500'}`}></div>
                                    <span className="text-sm font-bold text-slate-900">{user.username}</span>
                                </div>
                                {user.is_admin && <span className="text-[10px] font-bold text-red-800 bg-red-50 px-2 py-0.5 rounded uppercase">Admin</span>}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminConsole;
