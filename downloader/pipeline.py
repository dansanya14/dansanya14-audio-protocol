def download_tracks(tracks, controller, logger):
    total_tracks = len(tracks)
    succeeded, failed, skipped = [], [], []

    controller.start_batch(total_tracks)

    for index, track in enumerate(tracks, start=1):
        if not controller.should_continue():
            logger.log_message("Download cancelled by user.", "WARNING")
            break

        while controller.paused:
            time.sleep(1)

        search_query = f"{track['artist']} - {track['title']}"
        logger.log_message(f"({index}/{total_tracks}) Resolving YouTube: {search_query}", "INFO")

        # Skip if file exists
        if file_exists(track, base_dir=controller.download_dir):
            logger.log_message(f"File already exists: {search_query}. Skipping.", "WARNING")
            skipped.append(track)
            continue

        # Resolve URL
        resolved_url = resolve_youtube_url(search_query, logger)
        if not resolved_url or "youtube.com" not in resolved_url:
            logger.log_message(f"Failed to resolve YouTube URL for {search_query}", "ERROR")
            failed.append(track)
            continue

        # Download audio
        output_template = os.path.join(controller.download_dir, "%(title)s.%(ext)s")
        success = download_audio(resolved_url, output_template, logger)
        if success is None:
            failed.append(track)
            continue

        # Find downloaded FLAC
        flac_file = file_exists(track, return_path=True, base_dir=controller.download_dir)
        if not flac_file:
            logger.log_message(f"Download complete, but FLAC not found: {search_query}", "ERROR")
            failed.append(track)
            continue

        # Embed thumbnail (safe)
        try:
            video_id = extract_video_id(resolved_url)
            image_data = download_thumbnail(video_id)
            if image_data:
                embed_thumbnail(flac_file, image_data)
        except Exception as e:
            logger.log_message(f"Thumbnail embedding failed: {e}", "WARNING")

        # Tag metadata (safe defaults)
        title = clean_title(track.get("title") or "Unknown Title")
        artist = track.get("artist") or "Unknown Artist"
        album = track.get("album") or "Unknown Album"

        try:
            tag_audio(flac_file, {"title": title, "artist": artist, "album": album})
        except Exception as e:
            logger.log_message(f"Metadata tagging failed: {e}", "WARNING")

        # Captions (safe)
        try:
            if has_manual_subs(resolved_url, lang="en"):
                srt_path = flac_file.replace(".flac", ".en.srt")
                lyrics = extract_clean_captions(srt_path)
                if lyrics:
                    embed_captions(flac_file, lyrics)
        except Exception as e:
            logger.log_message(f"Captions embedding failed: {e}", "WARNING")

        logger.log_message(f"Downloaded and processed: {search_query}", "SUCCESS")
        succeeded.append(track)

        controller.update_progress(index / total_tracks)
        controller.update_speed(tracks_done=index, total_tracks=total_tracks)

    # Batch summary
    logger.log_message(
        f"Finished: {len(succeeded)} succeeded, {len(failed)} failed, {len(skipped)} skipped",
        "INFO"
    )

    # Persist failed tracks
    if failed:
        os.makedirs("logs", exist_ok=True)
        try:
            with open(FAILED_TRACKS_FILE, "w", encoding="utf-8") as f:
                json.dump(failed, f, indent=2)
            logger.log_message(f"Saved {len(failed)} failed track(s) to {FAILED_TRACKS_FILE}", "INFO")
        except Exception as e:
            logger.log_message(f"Could not save failed tracks: {e}", "ERROR")

    return {"succeeded": succeeded, "failed": failed, "skipped": skipped}