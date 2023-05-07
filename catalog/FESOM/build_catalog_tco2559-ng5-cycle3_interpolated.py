import os
import glob
import intake
import yaml

out_catalog_name = "tco2559-ng5-cycle3_interpolated.yaml"


def create_intake_catalog():
    resolutions = {
        "1_degree_monthly": "/scratch/a/a270046/cycle3/extracted/tco2559-ng5",
        "025_degree_monthly": "/scratch/a/a270046/cycle3/extracted/tco2559-ng5/moda/",
    }

    catalog_entries = {}
    variable_lists = {}

    for resolution, path in resolutions.items():
        if os.path.exists(path):
            for nc_file in glob.glob(f"{path}/*.nc"):
                file_name = os.path.basename(nc_file)
                variable_name = file_name.split(".")[0]
                if resolution not in catalog_entries:
                    catalog_entries[resolution] = {
                        "driver": "netcdf",
                        "args": {"urlpath": []},
                        "metadata": {"resolution": resolution},
                    }
                    variable_lists[resolution] = []
                catalog_entries[resolution]["args"]["urlpath"].append(nc_file)
                variable_lists[resolution].append(variable_name)

    # Save catalog to YAML file
    with open(out_catalog_name, "w") as outfile:
        # Write comments at the beginning of the file
        outfile.write("# Available variables per resolution:\n")
        for resolution, variables in variable_lists.items():
            outfile.write(f"# - {resolution}: {', '.join(variables)}\n")
        outfile.write("\n")

        # Write plugins entry
        yaml.dump(
            {"plugins": {"source": [{"module": "intake_xarray"}]}},
            outfile,
            default_flow_style=False,
        )

        # Add the 'sources' key and dump YAML content to the file
        yaml.dump({"sources": catalog_entries}, outfile, default_flow_style=False)

    # Load and return the catalog
    return intake.open_catalog(out_catalog_name)


# Run the function and create the catalog
catalog = create_intake_catalog()
