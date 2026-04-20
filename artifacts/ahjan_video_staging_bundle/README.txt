Ahjan video staging bundle (for import into brand-wizard-app/public/assets/video/)
===================================================================================

staging_teacher_vid_package/ahjan.mp4
  Source: git teacher_vid_package/ahjan.mp4 (commit + LFS in repo)
  Next: copy into e.g. brand-wizard-app/public/assets/video/teacher_reels/ with a final name, then git add (Git LFS).

documents_downloads/
  Copies from ~/Documents/Downloads/ at pack build time.
  Not in git until you import under public/assets/video/…

Suggested public names (snake_case) after you review:
  ahjan_teaching_documents.mp4  (from Ahjan Teaching.mp4)
  ahjan_sangha_satsang_2023-04-09.mp4
  ahjan_chatgpt_online_income_blueprint.mp4

Regenerate this folder + zip:
  bash scripts/brand_admin/build_ahjan_video_staging_bundle.sh
