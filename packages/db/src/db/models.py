# (same file content as before — only showing PainCluster part modified)

# Add inside PainCluster:

    # EPIC 04
    cluster_summary = Column(Text, nullable=True)
    top_signal_ids_json = Column(Text, nullable=False, server_default="[]")
    key_phrases_json = Column(Text, nullable=False, server_default="[]")
    confidence_score = Column(Integer, nullable=False, server_default="0", index=True)
