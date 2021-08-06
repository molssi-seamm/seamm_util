# -*- coding: utf-8 -*-

"""Interact with Zenodo via its REST API

"""

import pprint
import requests


upload_types = {
    "publication": "Publication",
    "poster": "Poster",
    "presentation": "Presentation",
    "dataset": "Dataset",
    "image": "Image",
    "video": "Video/Audio",
    "software": "Software",
    "lesson": "Lesson",
    "physicalobject": "Physical object",
    "other": "Other",
}


class Record(object):
    """A class for handling uploading a record to Zenodo.

    Attributes
    ----------
    data : dict()
        The record data from Zenodo. See https://developers.zenodo.org/#depositions
    token : str
        The Zenodo access token for the user.
    metadata : dict()
        The metadata for updating the record.
    """
    
    def __init__(self, data, token):
        self.data = data
        self.token = token
        self.metadata = {}

    @property
    def creators(self):
        """The creators for the record."""
        if "creators" not in self.metadata:
            if "creators" in self.data["metadata"]:
                self.metadata["creators"] = [*self.data["metadata"]["creators"]]
            else:
                self.metadata["creators"] = []
        return self.metadata["creators"]

    @property
    def description(self):
        """The description for the record."""
        if "description" not in self.metadata:
            if "description" in self.data["metadata"]:
                self.metadata["description"] = self.data["metadata"]["description"]
            else:
                return None
        return self.metadata["description"]

    @description.setter
    def description(self, value):
        self.metadata["description"] = value

    @property
    def doi(self):
        """The (prereserved) DOI."""
        if "doi" in self.data:
            return self.data["doi"]
        else:
            return self.data["metadata"]["prereserve_doi"]["doi"]

    @property
    def in_progress(self):
        """Whether the deposition is still in progress, i.e. editable.

        Returns
        -------
        bool
        """
        return self.data["state"] == "inprogress"

    @property
    def keywords(self):
        """The keywords for the record."""
        if "keywords" not in self.metadata:
            if "keywords" in self.data["metadata"]:
                self.metadata["keywords"] = [*self.data["metadata"]["keywords"]]
            else:
                self.metadata["keywords"] = []
        return self.metadata["keywords"]

    @property
    def submitted(self):
        """Whether the record has been submitted.

        If so the files can't be changed, but it may be possible to edit the metadata.

        Returns
        -------
        bool
        """
        return self.data["submitted"]

    @property
    def title(self):
        """The title for the record."""
        if "title" not in self.metadata:
            if "title" in self.data["metadata"]:
                self.metadata["title"] = self.data["metadata"]["title"]
            else:
                return None
        return self.metadata["title"]

    @title.setter
    def title(self, value):
        self.metadata["title"] = value

    @property
    def upload_type(self):
        """The type of record in Zenodo."""
        if "upload_type" not in self.metadata:
            if "upload_type" in self.data["metadata"]:
                self.metadata["upload_type"] = self.data["metadata"]["upload_type"]
            else:
                return None
        return self.metadata["upload_type"]

    @upload_type.setter
    def upload_type(self, value):
        if value not in Record.upload_types:
            raise ValueError(
                f"upload_type '{value}' must be one of "
                f"{', '.join(Record.upload_types.keys())}"
            )
        self.metadata["upload_type"] = value

    def add_creator(self, name, affiliation=None, orcid=None):
        """Add a creator (author) to the record.

        Parameters
        ----------
        name : str
            The creators name as "family name, other names"
        affiliation : str, optional
            The creators affiliation (University, company,...)
        orcid : str, optional
            The ORCID id of the creator.
        """
        # Already exists?
        for creator in self.creators:
            if "orcid" in creator and orcid is None:
                if creator["orcid"] == orcid:
                    raise RuntimeError(f"Duplicate entry for creator: {name}")
            elif creator["name"] == name:
                raise RuntimeError(f"Duplicate entry for creator: {name}")

        creator = {"name": name}
        if affiliation is not None:
            creator["affiliation"] = affiliation
        if orcid is not None:
            creator["orcid"] = orcid
        self.metadata["creators"].append(creator)

    def add_file(self, path, binary=False):
        """Add the given file to the record.

        Parameters
        ----------
        path : pathlib.Path
            The path to the file to upload.
        binary : bool = False
            Whether to open as a binary file.
        """
        if self.submitted:
            raise RuntimeError("Files cannot be added to a submitted record.")

        url = self.data["links"]["bucket"] + "/" + path.name
        headers = {"Authorization": f"Bearer {self.token}"}
        mode = "rb" if binary else "r"
        with open(path, mode) as fd:
            response = requests.put(url, data=fd, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Error in add_file: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        # Add the new file to the metadata
        self.data["files"].append(response.json())

    def add_keyword(self, keyword):
        """Add a keyword to the record.

        Parameters
        ----------
        keyword : str
            The keyword
        """
        # Already exists?
        if keyword not in self.keywords:
            self.metadata["keywords"].append(keyword)


    def download_file(self, filename, path):
        """Download a file to a local copy.

        Parameters
        ----------
        filename : str
            The name of the file.
        path : pathlib.Path
            The path to download the file to. Can be a directory in which case
            the filename is used in that directory.
        
        Returns
        -------
        pathlib.Path
            The path to the downloaded file.
        """
        if "files" not in self.data:
            raise RuntimeError("There are no files in the record.")

        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            out_path = path / filename
        else:
            out_path = path

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

        for data in self.data["files"]:
            if data["filename"] == filename:
                url = data["links"]["download"]
                response = requests.get(url, headers=headers, stream=True)

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Error in download_file: code = {response.status_code}"
                        f"\n\n{pprint.pformat(response.json())}"
                    )

                with open(out_path, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=128):
                        fd.write(chunk)

                return out_path

        raise RuntimeError(f"File '{filename}' is not part of the deposit.")

    def files(self):
        """List of the files deposited.

        Returns
        -------
        [str]
        """
        if "files" in self.data:
            return [x["filename"] for x in self.data["files"]]
        else:
            return []

    def get_file(self, filename):
        """Get the contents of a file.

        Parameters
        ----------
        filename : str
            The name of the file.
        
        Returns
        -------
        str or byte
        """
        if "files" not in self.data:
            raise RuntimeError("There are no files in the record.")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

        for data in self.data["files"]:
            if data["filename"] == filename:
                url = data["links"]["download"]
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Error in get_file: code = {response.status_code}"
                        f"\n\n{pprint.pformat(response.json())}"
                    )
                return response.text

        raise RuntimeError(f"File '{filename}' is not part of the deposit.")

    def publish(self):
        """Publish the record on Zenodo.
        
        This registers the DOI, and after this the files cannot be changed.
        Any new metadata is uploaded before publishing.
        """
        if len(self.metadata) > 0:
            self.update_metadata()

        url = self.data["links"]["publish"]
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.post(url, headers=headers)

        if response.status_code != 202:
            raise RuntimeError(
                f"Error in publish_metadata: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        self.data = response.json()

    def remove_file(self, filename):
        """Remove a file.

        Parameters
        ----------
        filename : str
            The name of the file.
        """
        if self.submitted:
            raise RuntimeError("Files cannot be removed from a submitted record.")

        if "files" not in self.data:
            raise RuntimeError("There are no files in the record.")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

        for index, data in enumerate(self.data["files"]):
            if data["filename"] == filename:
                url = data["links"]["self"]
                response = requests.delete(url, headers=headers)

                if response.status_code != 204:
                    raise RuntimeError(
                        f"Error in remove_file: code = {response.status_code}"
                        f"\n\n{pprint.pformat(response.json())}"
                    )

                # Remove the entry from the metadata
                del self.data["files"][index]

                return

        raise RuntimeError(f"File '{filename}' is not part of the deposit.")

    def remove_keyword(self, keyword):
        """Remove a keyword from the record.

        Parameters
        ----------
        keyword : str
            The keyword
        """
        # Doesn't exist?
        if keyword not in self.keywords:
            self.metadata["keywords"].append(keyword)

    def update_metadata(self):
        """Update the metadata for the record in Zenodo."""
        url = self.data["links"]["self"]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

        data = {"metadata": self.metadata}
        data = json.dumps(data)

        response = requests.put(url, data=data, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Error in update_metadata: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        self.data = response.json()
        self.metadata = {}


class Zenodo(object):
    def __init__(self, token, use_sandbox=False):
        if use_sandbox:
            self.base_url = "https://sandbox.zenodo.org/api"
        else:
            self.base_url = "https://zenodo.org/api"
        self.token = token

    def add_version(self, _id):
        """Create a new record object for uploading a new version to Zenodo."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

        url = self.base_url + f"/deposit/depositions/{_id}/actions/newversion"
        response = requests.post(url, headers=headers)

        if response.status_code != 201:
            raise RuntimeError(
                f"Error in add_version: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        result = response.json()

        # The result is for the original DOI, so get the data for the new one
        url = result["links"]["latest_draft"]
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Error in add_version get latest draft: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        result = response.json()

        return Record(result, self.token)

    def create_record(self):
        """Create a new record object for uploading to Zenodo."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

        url = self.base_url + "/deposit/depositions"
        response = requests.post(url, json={}, headers=headers)

        if response.status_code != 201:
            raise RuntimeError(
                f"Error in create_record: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        result = response.json()

        return Record(result, self.token)

    def get_record(self, _id):
        """Get an existing record object from Zenodo."""
        url = self.base_url + f"/deposit/depositions/{_id}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

        response = requests.get(url, json={}, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Error in get_record: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        result = response.json()

        return Record(result, self.token)

    def search(self, communities=None, keywords=None, size=100, page=1):
        """Search for records in Zenodo."""
        url = self.base_url + "/records"
        headers = {"Authorization": f"Bearer {self.token}"}

        payload = {
            "size": size,
            "page": page,
        }
        q = []
        if communities is not None:
            for community in communities:
                q.append(f'+communities:"{community}"')

        if keywords is not None:
            for keyword in keywords:
                q.append(f'+keywords:"{keyword}"')

        if len(q) > 0:
            payload["q"] = " ".join(q)

        response = requests.get(url, headers=headers, params=payload)

        if response.status_code != 200:
            raise RuntimeError(
                f"Error in search: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        result = response.json()

        records = []
        if "hits" in result:
            hits = result["hits"]

            n_hits = hits["total"]
            for record in hits["hits"]:
                records.append(Record(record, self.token))

            print(f"Found {len(records)} ({n_hits}) records")
            for record in records:
                print(f"\t{record['id']}: {record['metadata']['title']}")

        return records
