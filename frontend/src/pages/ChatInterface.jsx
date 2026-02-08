import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { api, authHeaders } from '../services/api';
import {
    PaperClipIcon,
    ArrowUpIcon,
    DocumentIcon,
    XMarkIcon,
    Square3Stack3DIcon,
    ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';

const ChatInterface = () => {
    const { t } = useTranslation();
    const isRTL = document.documentElement.dir === 'rtl';
    const [chats, setChats] = useState([]);
    const [activeChat, setActiveChat] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef(null);

    const config = { headers: authHeaders() };

    useEffect(() => {
        fetchChats();
    }, []);

    useEffect(() => {
        if (activeChat) {
            fetchMessages(activeChat.id);
        }
    }, [activeChat]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const fetchChats = async () => {
        try {
            const res = await api.get('/chats', config);
            setChats(res.data);
            if (res.data.length > 0 && !activeChat) {
                setActiveChat(res.data[0]);
            }
        } catch (err) {
            console.error('Failed to fetch chats');
        }
    };

    const fetchMessages = async (chatId) => {
        try {
            const res = await api.get(`/chats/${chatId}/messages`, config);
            setMessages(res.data);
        } catch (err) {
            console.error('Failed to fetch messages');
        }
    };

    const createNewChat = async () => {
        const title = `${t('chat.newCaseStudy')} ${chats.length + 1}`;
        try {
            const res = await api.post('/chats', { title }, config);
            setChats([...chats, res.data]);
            setActiveChat(res.data);
            setMessages([]);
        } catch (err) {
            console.error('Failed to create chat');
        }
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputText.trim() || !activeChat) return;

        const userMessage = { sender: 'user', content: inputText, timestamp: new Date() };
        setMessages([...messages, userMessage]);
        setInputText('');
        setIsTyping(true);

        try {
            const res = await api.post('/chat/ask', {
                chat_id: activeChat.id,
                content: inputText
            }, config);

            setMessages(prev => [...prev, {
                sender: 'ai',
                content: res.data.response,
                timestamp: new Date()
            }]);
        } catch (err) {
            console.error('Failed to ask AI');
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className={`flex bg-white h-full -m-6 rounded-xl overflow-hidden shadow-2xl border border-slate-200 ${isRTL ? 'flex-row-reverse' : ''}`}>
            {/* Sidebar for Case Chat */}
            <div className={`w-64 ${isRTL ? 'border-l border-slate-100' : 'border-r border-slate-100'} flex flex-col bg-slate-50/10`}>
                <div className="p-6">
                    <button
                        onClick={createNewChat}
                        className={`w-full bg-red-900 text-white py-3 rounded-xl text-sm font-bold flex items-center justify-center ${isRTL ? 'space-x-reverse space-x-2' : 'space-x-2'} shadow-sm`}
                    >
                        <span className="text-xl">+</span>
                        <span>{t('chat.newCaseStudy')}</span>
                    </button>
                </div>

                <div className="flex-grow p-6 pt-0 overflow-y-auto">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-4">{t('chat.recentInvestigations')}</p>
                    <div className="space-y-4">
                        {chats.map((chat) => (
                            <div
                                key={chat.id}
                                onClick={() => setActiveChat(chat)}
                                className={`p-3 rounded-xl cursor-pointer transition-all ${activeChat?.id === chat.id
                                        ? `border border-red-200 bg-red-50 ${isRTL ? 'border-r-4 border-r-red-800' : 'border-l-4 border-l-red-800'}`
                                        : 'hover:bg-slate-50'
                                    }`}
                            >
                                <div className={`text-xs font-bold ${activeChat?.id === chat.id ? 'text-slate-800' : 'text-slate-600'}`}>
                                    {chat.title}
                                </div>
                                <div className="text-[10px] text-slate-400">
                                    {new Date(chat.created_at).toLocaleDateString()}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="p-6 border-t border-slate-100">
                    <div className="bg-red-50 p-4 rounded-xl border border-red-100">
                        <div className="text-[10px] font-bold text-red-800 uppercase mb-1">{t('chat.proPlan')}</div>
                        <div className="text-[10px] text-slate-500 mb-3">{t('chat.documentsUsed')}</div>
                        <button className="w-full py-2 bg-white border border-slate-200 text-[10px] font-bold rounded-lg uppercase tracking-tight shadow-sm hover:bg-slate-50">{t('chat.upgradePlan')}</button>
                    </div>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-grow flex flex-col relative bg-slate-50/10">
                <div className={`h-16 border-b border-slate-100 px-8 flex items-center ${isRTL ? 'flex-row-reverse justify-between' : 'justify-between'} bg-white`}>
                    <div className={`flex items-center ${isRTL ? 'space-x-reverse space-x-4' : 'space-x-4'}`}>
                        <div>
                            <h2 className="text-sm font-bold text-slate-800">
                                {activeChat ? `${t('chat.case')}: ${activeChat.title}` : t('chat.selectCaseStudy')}
                            </h2>
                            <div className={`flex items-center ${isRTL ? 'space-x-reverse space-x-2' : 'space-x-2'} text-[10px] text-slate-400`}>
                                <span className="bg-green-100 text-green-700 px-1.5 rounded font-bold">{t('chat.indexed')}</span>
                                <span>{t('chat.ragEngineReady')} • {t('chat.vllmInfrastructureActive')}</span>
                            </div>
                        </div>
                    </div>
                    <div className={`flex ${isRTL ? 'space-x-reverse space-x-2' : 'space-x-2'}`}>
                        <button className={`flex items-center ${isRTL ? 'space-x-reverse space-x-2' : 'space-x-2'} px-3 py-1.5 border border-slate-200 rounded-lg text-xs font-bold text-slate-600 hover:bg-slate-50`}>
                            <span>{t('common.export')}</span>
                        </button>
                    </div>
                </div>

                <div className="flex-grow p-8 overflow-y-auto space-y-8" ref={scrollRef}>
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-30 grayscale">
                            <ChatBubbleLeftIcon className="h-16 w-16 text-slate-400" />
                            <div>
                                <p className="text-sm font-bold">{t('chat.startInvestigation')}</p>
                                <p className="text-xs">{t('chat.askQuestion')}</p>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.sender === 'user' ? (isRTL ? 'justify-start' : 'justify-end') : (isRTL ? 'justify-end' : 'justify-start')}`}>
                            {msg.sender === 'ai' ? (
                                <div className={`flex ${isRTL ? 'space-x-reverse space-x-4 flex-row-reverse' : 'space-x-4'} max-w-4xl`}>
                                    <div className="w-8 h-8 rounded-lg bg-red-900 flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                                        <div className="text-white text-xs font-bold">A</div>
                                    </div>
                                    <div className="space-y-4">
                                        <div className={`flex items-center ${isRTL ? 'space-x-reverse space-x-2 flex-row-reverse' : 'space-x-2'}`}>
                                            <span className="text-xs font-bold text-slate-900">{t('chat.scalovateAI')}</span>
                                            <span className="text-[10px] text-slate-400">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        </div>
                                        <div className={`bg-white border border-slate-100 p-6 rounded-2xl shadow-sm space-y-4 ${isRTL ? 'text-right' : 'text-left'}`}>
                                            <p className={`text-sm text-slate-800 leading-relaxed font-normal whitespace-pre-wrap ${isRTL ? 'text-right' : 'text-left'}`}>{msg.content}</p>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className={`flex ${isRTL ? 'space-x-reverse space-x-4 flex-row-reverse' : 'space-x-4'} max-w-2xl`}>
                                    <div className={`space-y-2 ${isRTL ? 'text-left' : 'text-right'}`}>
                                        <div className={`flex items-center ${isRTL ? 'justify-start space-x-reverse space-x-2 flex-row-reverse' : 'justify-end space-x-2'}`}>
                                            <span className="text-[10px] text-slate-400">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                            <span className="text-xs font-bold text-slate-900">{t('chat.you')}</span>
                                        </div>
                                        <div className={`bg-red-900 text-white p-6 rounded-2xl shadow-lg shadow-red-900/10 text-sm leading-relaxed ${isRTL ? 'text-right' : 'text-left'}`}>
                                            {msg.content}
                                        </div>
                                    </div>
                                    <div className="w-8 h-8 rounded-lg bg-teal-100 flex items-center justify-center flex-shrink-0 mt-1 border border-teal-200">
                                        <img src={`https://ui-avatars.com/api/?name=${localStorage.getItem('username')}&background=3dd2cc&color=fff`} className="w-full h-full rounded-lg" alt="User" />
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}

                    {isTyping && (
                        <div className={`flex ${isRTL ? 'space-x-reverse space-x-4 flex-row-reverse' : 'space-x-4'} max-w-4xl`}>
                            <div className="w-8 h-8 rounded-lg bg-red-900 flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                                <div className="text-white text-xs font-bold">A</div>
                            </div>
                            <div className="space-y-4">
                                <div className={`flex items-center ${isRTL ? 'space-x-reverse space-x-3 flex-row-reverse' : 'space-x-3'}`}>
                                    <div className={`flex ${isRTL ? 'space-x-reverse space-x-1' : 'space-x-1'}`}>
                                        <div className="w-1.5 h-1.5 bg-red-800 rounded-full animate-bounce"></div>
                                        <div className="w-1.5 h-1.5 bg-red-800 rounded-full animate-bounce delay-100"></div>
                                        <div className="w-1.5 h-1.5 bg-red-800 rounded-full animate-bounce delay-200"></div>
                                    </div>
                                    <span className="text-xs italic text-slate-500 font-medium">{t('chat.analyzingDocuments')}</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-8 pt-0">
                    <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto relative group">
                        <div className="absolute inset-0 bg-red-800/10 rounded-2xl blur-xl transition-all group-focus-within:bg-red-800/20"></div>
                        <div className="relative border border-slate-200 rounded-2xl bg-white shadow-xl overflow-hidden focus-within:ring-2 focus-within:ring-red-900/20 transition-all">
                            <div className={`flex items-center p-4 ${isRTL ? 'pl-6' : 'pr-6'}`}>
                                <button type="button" className="p-2 text-slate-400 hover:text-red-900 transition-colors">
                                    <PaperClipIcon className="h-5 w-5" />
                                </button>
                                <input
                                    type="text"
                                    placeholder={t('chat.askAboutCase')}
                                    className={`flex-grow bg-transparent border-none focus:ring-0 text-sm py-4 px-4 text-slate-800 font-medium placeholder:text-slate-300 ${isRTL ? 'text-right' : 'text-left'}`}
                                    value={inputText}
                                    onChange={(e) => setInputText(e.target.value)}
                                    disabled={!activeChat}
                                    dir={isRTL ? 'rtl' : 'ltr'}
                                />
                                <button
                                    type="submit"
                                    disabled={!activeChat || !inputText.trim()}
                                    className="bg-red-950 p-2.5 rounded-xl text-white shadow-lg shadow-red-950/40 hover:scale-105 active:scale-95 transition-all disabled:opacity-50"
                                >
                                    <ArrowUpIcon className="h-5 w-5" />
                                </button>
                            </div>
                            <div className={`flex items-center ${isRTL ? 'space-x-reverse space-x-6 flex-row-reverse' : 'space-x-6'} px-4 py-2 bg-slate-50/50 border-t border-slate-50 text-[10px] font-bold text-slate-400`}>
                                <button type="button" className={`flex items-center ${isRTL ? 'space-x-reverse space-x-1 flex-row-reverse' : 'space-x-1'} hover:text-slate-600 transition-colors`}>
                                    <span>📝</span>
                                    <span>{t('chat.draftSummary')}</span>
                                </button>
                                <button type="button" className={`flex items-center ${isRTL ? 'space-x-reverse space-x-1 flex-row-reverse' : 'space-x-1'} hover:text-slate-600 transition-colors`}>
                                    <span>⚖️</span>
                                    <span>{t('chat.checkCompliance')}</span>
                                </button>
                                <div className={`${isRTL ? 'mr-auto' : 'ml-auto'} italic text-slate-300 font-normal`}>{t('chat.aiDisclaimer')}</div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>

            {/* Source Inspector Panel (Static for UI Parity) */}
            <div className={`w-80 ${isRTL ? 'border-r border-slate-100' : 'border-l border-slate-100'} flex flex-col bg-white`}>
                <div className={`p-6 h-16 border-b border-slate-100 flex items-center ${isRTL ? 'flex-row-reverse justify-between' : 'justify-between'}`}>
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide">{t('chat.sourceInspector')}</h3>
                    <XMarkIcon className="h-4 w-4 text-slate-300 cursor-pointer" />
                </div>
                <div className="p-6 space-y-6 flex-grow overflow-y-auto">
                    <div className={`border border-dashed border-slate-200 rounded-2xl p-8 flex flex-col items-center justify-center text-center space-y-4 bg-slate-50/30 ${isRTL ? 'text-right' : 'text-left'}`}>
                        <div className="w-12 h-12 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center text-red-900">
                            <DocumentIcon className="h-6 w-6" />
                        </div>
                        <div className={`text-[11px] font-medium text-slate-400 leading-normal px-4 ${isRTL ? 'text-right' : 'text-left'}`}>
                            {t('chat.sourcesAppear')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const ChatBubbleLeftIcon = (props) => <ChatBubbleLeftRightIcon {...props} />;

export default ChatInterface;
