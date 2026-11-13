"""Non-product check: validates initial SQLite migration and FTS triggers."""
from pathlib import Path
import sqlite3
root = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(':memory:')
conn.executescript((root / 'db' / '001_initial.sql').read_text(encoding='utf-8'))
conn.execute('PRAGMA foreign_keys=ON')
assert conn.execute('PRAGMA foreign_keys').fetchone()[0] == 1
conn.execute("INSERT INTO workspaces(id,name) VALUES('w','Test')")
conn.execute("INSERT INTO file_assets(id,sha256,original_path,byte_size) VALUES('a',?,'C:/fixture.pdf',0)", ('0'*64,))
conn.execute("INSERT INTO documents(id,workspace_id,title) VALUES('d','w','Fixture')")
conn.execute("INSERT INTO document_versions(id,document_id,file_asset_id,version_no) VALUES('v','d','a',1)")
conn.execute("INSERT INTO pages(id,document_version_id,page_index,width,height) VALUES('p','v',0,612,792)")
conn.execute("INSERT INTO content_blocks(id,page_id,block_index,block_type,text,bbox_json,reading_order) VALUES('b','p',0,'paragraph','Hop dong xay dung','[10,10,100,20]',0)")
assert conn.execute("SELECT count(*) FROM content_blocks_fts WHERE content_blocks_fts MATCH 'Hop'").fetchone()[0] == 1
assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
print('PASS: SQL migrations, FK, FTS insert/query, integrity')
