"""
MediBot - Chatbot Informasi RS Sehat Sentosa (Streamlit version)
Menggunakan Groq API (gratis, cepat, tidak perlu kartu kredit)

Cara menjalankan:
    1. pip install -r requirements.txt
    2. Buat akun Groq: https://console.groq.com
    3. Set environment variable GROQ_API_KEY
       Linux/Mac:  export GROQ_API_KEY="your-key-here"
       Windows:    set GROQ_API_KEY=your-key-here
    4. streamlit run app.py
"""

import os
import streamlit as st
from groq import Groq

# ---------- Konfigurasi halaman ----------
st.set_page_config(
    page_title="MediBot — RS Sehat Sentosa",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- Knowledge base / system prompt ----------
SYSTEM_PROMPT = """Kamu adalah MediBot, asisten virtual ramah untuk RS Sehat Sentosa, rumah sakit umum modern di Indonesia.

Tugasmu memberi informasi yang jelas, hangat, dan akurat tentang:

**Layanan & Poliklinik**
- IGD 24 jam (selalu buka)
- Poli Umum: Senin–Sabtu 08:00–20:00
- Poli Anak: Senin–Jumat 08:00–14:00 & 16:00–20:00, Sabtu 08:00–12:00
- Poli Kandungan & Kebidanan: Senin–Sabtu 09:00–17:00
- Poli Jantung: Senin, Rabu, Jumat 09:00–15:00
- Poli Gigi: Senin–Sabtu 09:00–17:00
- Poli Mata, THT, Kulit, Saraf, Penyakit Dalam, Bedah, Ortopedi
- Medical Check Up, Fisioterapi, Hemodialisa
- Laboratorium & Radiologi (Rontgen, USG, CT Scan, MRI) 24 jam

**Dokter Praktek (contoh)**
- dr. Andi Pratama, Sp.JP — Jantung (Sen/Rab/Jum, 09–15)
- dr. Sinta Wijaya, Sp.A — Anak (Sen–Jum)
- dr. Budi Hartono, Sp.OG — Kandungan
- dr. Maya Lestari, Sp.PD — Penyakit Dalam
- drg. Rama Saputra — Gigi Umum

**Pendaftaran**
- Online via website/aplikasi RS Sehat Sentosa, WhatsApp 0811-2345-678, atau langsung di loket.
- Bawa: KTP, kartu BPJS/asuransi (jika ada), rujukan dari Faskes 1 (untuk BPJS non-emergensi).

**Pembayaran & Asuransi**
- Tunai, debit, kartu kredit, QRIS.
- BPJS Kesehatan, Mandiri Inhealth, Allianz, AXA, Prudential, Cigna, dan asuransi lain (konfirmasi ke admisi).

**Fasilitas**
- IGD 24 jam, ICU, NICU, PICU, ruang operasi, kamar VIP/Kelas 1/2/3, apotek 24 jam, kantin, parkir luas, ambulans 24 jam.

**Kontak**
- Alamat: Jl. Sehat Raya No. 123, Jakarta Selatan
- Telp: (021) 555-7890
- WhatsApp: 0811-2345-678
- Email: info@rs-sehatsentosa.co.id
- Website: www.rs-sehatsentosa.co.id

**Aturan Penting:**
1. Jawab dalam Bahasa Indonesia yang ramah dan profesional. Gunakan markdown (bullet, bold) agar mudah dibaca.
2. Untuk keluhan medis: JANGAN memberi diagnosis atau resep. Sarankan konsultasi langsung ke dokter / IGD jika darurat.
3. Untuk keadaan darurat (nyeri dada hebat, sesak berat, kecelakaan, pendarahan, stroke), arahkan segera ke IGD 24 jam atau telp (021) 555-7890.
4. Jika ditanya hal di luar info RS, jawab singkat lalu tawarkan bantuan terkait layanan RS.
5. Jika info tidak diketahui pasti, jujur katakan dan sarankan menghubungi (021) 555-7890.
"""

SUGGESTIONS = [
    "Jam praktek poli anak hari ini?",
    "Cara daftar pakai BPJS",
    "Jadwal dokter spesialis jantung",
    "Alamat dan kontak IGD",
]

# ---------- Initialize Groq Client ----------
@st.cache_resource
def get_groq_client():
    """Initialize Groq client"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def stream_reply(client, messages):
    """Stream balasan AI token-per-token menggunakan Groq"""
    try:
        stream = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            stream=True,
            temperature=0.7,
            max_tokens=1024,
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                delta = chunk.choices[0].delta.content
                full_response += delta
                yield delta
        return full_response
    except Exception as e:
        yield f"❌ Error: {str(e)}"
        return ""

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🏥 RS Sehat Sentosa")
    st.caption("Asisten Informasi 24/7")
    st.divider()

    st.markdown("**Kontak Cepat**")
    st.markdown(
        """
- 🚑 **IGD 24 jam**: (021) 555-7890
- 💬 **WhatsApp**: 0811-2345-678
- 📍 Jl. Sehat Raya No. 123, Jakarta Selatan
- 🌐 www.rs-sehatsentosa.co.id
        """
    )
    st.divider()

    if st.button("🗑️ Bersihkan percakapan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(
        "ℹ️ Informasi umum, bukan pengganti konsultasi medis. "
        "Untuk keadaan darurat, segera hubungi IGD."
    )

# ---------- Header ----------
col1, col2 = st.columns([1, 6])
with col1:
    st.markdown("<div style='font-size:48px;text-align:center'>🏥</div>", unsafe_allow_html=True)
with col2:
    st.markdown("## MediBot")
    st.caption("Asisten Informasi RS Sehat Sentosa · Online 24/7")

st.divider()

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

client = get_groq_client()

# ---------- Pesan kesalahan jika tidak ada API key ----------
if client is None:
    st.error(
        "❌ **GROQ_API_KEY belum diset.** \n\n"
        "**Cara setup:**\n"
        "1. Buka https://console.groq.com\n"
        "2. Sign up dengan email\n"
        "3. Buat API key di tab 'API Keys'\n"
        "4. Copy key-nya\n"
        "5. Di Streamlit Cloud → Settings → Secrets, paste:\n"
        "```\n"
        "GROQ_API_KEY=\"your-api-key-here\"\n"
        "```\n"
        "6. Klik Save & app akan auto-restart\n\n"
        "**Atau untuk local testing:**\n"
        "```bash\n"
        "export GROQ_API_KEY=\"your-key\"\n"
        "streamlit run app.py\n"
        "```"
    )
    st.stop()

# ---------- Empty state dengan saran ----------
if not st.session_state.messages:
    st.info("👋 Halo, saya **MediBot**. Tanyakan apa saja tentang layanan, jadwal dokter, pendaftaran, atau kontak RS Sehat Sentosa.")
    st.markdown("**Coba tanyakan:**")
    cols = st.columns(2)
    for i, s in enumerate(SUGGESTIONS):
        if cols[i % 2].button(s, key=f"sug_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": s})
            st.rerun()

# ---------- Render riwayat ----------
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🩺"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------- Jika pesan terakhir dari user dan belum dijawab → stream balasan ----------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🩺"):
        try:
            reply = st.write_stream(stream_reply(client, st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Gagal terhubung ke Groq: {e}")

# ---------- Composer ----------
prompt = st.chat_input("Tanyakan jadwal dokter, layanan, atau cara daftar…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
